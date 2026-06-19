import asyncio
import logging
import random

from aiohttp import ClientSession
from dishka_faststream import FromDishka
from faststream import AckPolicy, Context
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRouter

from src.app.dto.payments import PaymentUpdateStatusRequestDTO
from src.app.use_cases.change_payment_status import ChangePaymentStatusUseCase
from src.app.use_cases.set_payment_delivery import SetPaymentDeliveryUseCase
from src.core import settings
from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.infra.messaging.events.emitted import PaymentCreatedEvent
from src.infra.messaging.events.emitted.events import PaymentProcessedEvent
from src.infra.messaging.topology import payments_exchange, retry_exchange, webhook_queue

logging.basicConfig(level=settings.LOGGING.LEVEL, format=settings.LOGGING.FORMAT)
logger = logging.getLogger(__name__)
router = RabbitRouter()


@router.subscriber(queue=settings.MESSAGING.PAYMENTS.TOPICS.NEW, exchange=payments_exchange)
async def process_payment(
    event: PaymentCreatedEvent,
    use_case: FromDishka[ChangePaymentStatusUseCase],
    broker: RabbitBroker = Context(),
) -> None:
    await asyncio.sleep(random.uniform(2, 5))
    new_status = PaymentStatusEnum.SUCCESS if random.random() < 0.9 else PaymentStatusEnum.FAILED
    await use_case.execute(PaymentUpdateStatusRequestDTO(id=event.id, status=new_status))

    if event.webhook_url and new_status == PaymentStatusEnum.SUCCESS:
        message = PaymentProcessedEvent(status=new_status, **event.as_dict())
        await broker.publish(
            message=message.as_dict(),
            queue=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
            exchange="payments.exchange",
        )


@router.subscriber(queue=webhook_queue, exchange=payments_exchange, ack_policy=AckPolicy.MANUAL)
async def send_webhook_consumer(
    event: PaymentProcessedEvent,
    msg: RabbitMessage,
    http_client: FromDishka[ClientSession],
    use_case: FromDishka[SetPaymentDeliveryUseCase],
    broker: RabbitBroker = Context(),
) -> None:
    current_retry = get_retry_count(msg.headers)
    logger.info(f"Получен вебхук {event.id}. Текущая попытка (уже сделано ретраев): {current_retry}")

    if current_retry >= 3:
        logger.error(f"Превышен лимит ретраев ({current_retry}) для {event.id}. Отправляем в финальный DLQ.")
        await broker.publish(message=event.as_dict(), exchange=payments_exchange, routing_key="payments.webhooks.dead")
        await msg.ack()
        return

    try:
        logger.info(f"Отправка вебхука для {event.id} на URL {event.webhook_url}")

        payload = {"payment_id": str(event.id), "status": event.status}
        url = event.webhook_url.unicode_string()
        headers = {"X-Event-Id": str(event.event_id)}

        async with http_client.post(url, json=payload, timeout=10, headers=headers) as response:
            response.raise_for_status()
            logger.info(f"Вебхук успешно доставлен для {event.id}")
            await use_case.execute(event.id)
            await msg.ack()

    except Exception as exc:
        logger.warning(f"Ошибка при обработке {event.id}: {exc}. Отправляем в ретрай.")
        await send_to_exponential_retry(event, msg, current_retry, broker)


def get_retry_count(headers: dict) -> int:
    """Определяет номер текущей попытки по истории x-death."""
    x_death = headers.get("x-death", [])
    if not x_death:
        return 0

    for death in x_death:
        queue_name = death.get("queue")
        if queue_name == settings.MESSAGING.PAYMENTS.RETRY_POLICY.THIRD.RKEY:
            return 3
        if queue_name == settings.MESSAGING.PAYMENTS.RETRY_POLICY.SECOND.RKEY:
            return 2
        if queue_name == settings.MESSAGING.PAYMENTS.RETRY_POLICY.FIRST.RKEY:
            return 1
    return 0


async def send_to_exponential_retry(
    event: PaymentProcessedEvent, msg: RabbitMessage, current_retry: int, broker: RabbitBroker
) -> None:
    routing_keys = {
        0: settings.MESSAGING.PAYMENTS.RETRY_POLICY.FIRST.RKEY,
        1: settings.MESSAGING.PAYMENTS.RETRY_POLICY.SECOND.RKEY,
        2: settings.MESSAGING.PAYMENTS.RETRY_POLICY.THIRD.RKEY,
    }

    target_routing_key = routing_keys.get(current_retry, settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD)
    target_exchange = retry_exchange if current_retry < 3 else payments_exchange

    logger.info(f"Маршрутизация {event.id} в задержку через ключ: {target_routing_key}")

    await broker.publish(
        message=event.as_dict(),
        exchange=target_exchange,
        routing_key=target_routing_key,
        headers=msg.headers,
    )
    await msg.ack()
