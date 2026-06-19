import asyncio

from dishka_faststream import setup_dishka
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from src.containers import container
from src.core import settings
from src.infra.messaging.consumer import router
from src.infra.messaging.topology import (
    dead_queue,
    first_retry_queue,
    payments_exchange,
    retry_exchange,
    second_retry_queue,
    third_retry_queue,
    webhook_queue,
)

broker = RabbitBroker(settings.BROKER.dsn.unicode_string())
broker.include_router(router=router)
app = FastStream(broker)


@app.after_startup
async def setup_rabbit_infrastructure():
    exch_payments = await broker.declare_exchange(payments_exchange)
    exch_retry = await broker.declare_exchange(retry_exchange)

    q_webhook = await broker.declare_queue(webhook_queue)
    q_first = await broker.declare_queue(first_retry_queue)
    q_second = await broker.declare_queue(second_retry_queue)
    q_third = await broker.declare_queue(third_retry_queue)
    q_dead = await broker.declare_queue(dead_queue)

    await q_webhook.bind(exch_payments, routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS)

    await q_first.bind(exch_retry, routing_key=settings.MESSAGING.PAYMENTS.RETRY_POLICY.FIRST.RKEY)
    await q_second.bind(exch_retry, routing_key=settings.MESSAGING.PAYMENTS.RETRY_POLICY.SECOND.RKEY)
    await q_third.bind(exch_retry, routing_key=settings.MESSAGING.PAYMENTS.RETRY_POLICY.THIRD.RKEY)

    await q_dead.bind(exch_payments, routing_key=settings.MESSAGING.PAYMENTS.TOPICS.WEBHOOKS_DEAD)


async def main():
    setup_dishka(container=container, app=app, auto_inject=True)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
