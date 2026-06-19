from faststream.rabbit import ExchangeType, RabbitExchange
from faststream.rabbit.schemas.queue import ClassicQueueArgs, RabbitQueue

from src.core import settings

payments_exchange = RabbitExchange(name="payments.exchange", type=ExchangeType.DIRECT, durable=True)
retry_exchange = RabbitExchange(name="payments.retry_exchange", type=ExchangeType.DIRECT, durable=True)

webhook_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
)

first_retry_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.RETRY_POLICY.FIRST.RKEY,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.RETRY_POLICY.FIRST.RKEY,
    arguments=ClassicQueueArgs(**{
        "x-dead-letter-exchange": "payments.exchange",
        "x-dead-letter-routing-key": settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
        "x-message-ttl": settings.MESSAGING.PAYMENTS.RETRY_POLICY.FIRST.TIME,
    }),
)

second_retry_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.RETRY_POLICY.SECOND.RKEY,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.RETRY_POLICY.SECOND.RKEY,
    arguments=ClassicQueueArgs(**{
        "x-dead-letter-exchange": "payments.exchange",
        "x-dead-letter-routing-key": settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
        "x-message-ttl": settings.MESSAGING.PAYMENTS.RETRY_POLICY.SECOND.TIME,
    }),
)

third_retry_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.RETRY_POLICY.THIRD.RKEY,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.RETRY_POLICY.THIRD.RKEY,
    arguments=ClassicQueueArgs(**{
        "x-dead-letter-exchange": "payments.exchange",
        "x-dead-letter-routing-key": settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS,
        "x-message-ttl": settings.MESSAGING.PAYMENTS.RETRY_POLICY.THIRD.TIME,
    }),
)

dead_queue = RabbitQueue(
    name=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD,
    durable=True,
    routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD,
)
