import asyncio
import logging
import random

from aiohttp import ClientSession
from dishka_faststream import FromDishka
from faststream import AckPolicy, Context
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter

from src.app.dto.payments import PaymentUpdateStatusRequestDTO
from src.app.interfaces.units_of_work import ApplicationPaymentUnitOfWork
from src.app.use_cases.change_payment_status import ChangePaymentStatusUseCase
from src.app.use_cases.set_payment_processed import SetPaymentProcessedUseCase
from src.core import settings
from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.infra.adapters.brokers.topology import payments_exchange, webhook_queue
from src.infra.messaging.events.emitted import PaymentCreatedEvent
from src.infra.messaging.events.emitted.events import PaymentProcessedEvent
from src.infra.outbox.schemes import OutboxMessageScheme

logging.basicConfig(level=settings.LOGGING.LEVEL, format=settings.LOGGING.FORMAT)
logger = logging.getLogger(__name__)
router = RabbitRouter()


async def emulate_payment_processing() -> bool:
    delay = random.uniform(2, 5)
    await asyncio.sleep(delay)
    return random.random() < 0.9


@router.subscriber(queue=settings.MESSAGING.PAYMENTS.TOPICS.NEW, exchange=payments_exchange)
async def process_payment(
    event: PaymentCreatedEvent,
    c_use_case: FromDishka[ChangePaymentStatusUseCase],
    p_use_case: FromDishka[SetPaymentProcessedUseCase],
    uow: FromDishka[ApplicationPaymentUnitOfWork],
    message: RabbitMessage,
) -> None:
    payment_id: str = str(event.id)
    death_header = message.headers.get("x-death")
    retry_count = 0

    if death_header:
        retry_count = sum(d.get("count", 0) for d in death_header)

    if retry_count >= settings.MESSAGING.MAX_RETRIES:
        logger.error(
            "Payment %s exceeded max retries (%d). Dropping to DLQ.",
            payment_id,
            settings.MESSAGING.MAX_RETRIES,
        )
        await message.nack(requeue=False)
        return

    logger.info("Processing payment %s (retry=%d)", payment_id, retry_count)

    try:
        success = await emulate_payment_processing()
        new_status = PaymentStatusEnum.SUCCESS if success else PaymentStatusEnum.FAILED
        payment = PaymentUpdateStatusRequestDTO(id=event.id, status=new_status)
        await c_use_case.execute(payment)
        await p_use_case.execute(event.id)
        logger.info("Payment %s → %s", payment_id, new_status)

        if event.webhook_url:
            async with uow as uow:
                msg = OutboxMessageScheme(
                    body=PaymentProcessedEvent(status=new_status, **event.as_dict()).as_dict(),
                    topic=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
                )
                await uow.outbox.add_msgs(msg)
                await uow.commit()

    except Exception as exc:
        logger.exception("Unexpected error processing payment %s: %s", payment_id, exc)
        backoff = 2 ** (retry_count + 1)
        logger.info("Will requeue payment %s after %ds", payment_id, backoff)
        await asyncio.sleep(backoff)
        await message.nack(requeue=False)


@router.subscriber(queue=webhook_queue, exchange=payments_exchange, ack_policy=AckPolicy.MANUAL)
async def send_webhook_consumer(
    event: PaymentProcessedEvent, http_client: FromDishka[ClientSession], message: RabbitMessage
) -> None:
    payment_id = str(event.id)
    payload = {"payment_id": payment_id, "status": event.status}
    headers = {"X-Event-Id": str(event.event_id)}

    if event.webhook_url:
        url = event.webhook_url.unicode_string()
        for attempt in range(1, settings.MESSAGING.MAX_RETRIES + 1):
            try:
                async with http_client.post(url=url, json=payload, headers=headers, timeout=10) as response:
                    response.raise_for_status()
                    logger.info("Webhook sent for payment %s (attempt %d)", payment_id, attempt)
                    await message.ack()
                    return
            except Exception as exc:
                wait = 2**attempt
                logger.warning(
                    "Webhook failed for payment %s attempt %d: %s. Retrying in %ds", payment_id, attempt, exc, wait
                )
                if attempt < settings.MESSAGING.MAX_RETRIES:
                    await asyncio.sleep(wait)

    await message.nack(requeue=False)
    logger.error("Webhook exhausted retries for payment %s", payment_id)
