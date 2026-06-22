from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from src.core.settings import settings

payments_exchange = RabbitExchange(name="payments.exchange", type=ExchangeType.DIRECT, durable=True)
retry_exchange = RabbitExchange(name="payments.retry_exchange", type=ExchangeType.DIRECT, durable=True)

new_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.TOPICS.NEW,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.TOPICS.NEW,
)

webhook_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
)

dead_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD,
)


async def setup_rabbit_infrastructure(broker: RabbitBroker):
    exch_payments = await broker.declare_exchange(payments_exchange)

    q_new = await broker.declare_queue(new_queue)
    q_webhook = await broker.declare_queue(webhook_queue)
    q_dead = await broker.declare_queue(dead_queue)

    await q_new.bind(exch_payments, routing_key=settings.MESSAGING.PAYMENTS.TOPICS.NEW)
    await q_webhook.bind(exch_payments, routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS)
    await q_dead.bind(exch_payments, routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD)
