import asyncio

from dishka_faststream import setup_dishka
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from src.containers import container
from src.core import settings
from src.infra.adapters.brokers.topology import setup_rabbit_infrastructure
from src.infra.messaging.consumer import router

broker = RabbitBroker(settings.BROKER.dsn.unicode_string())
broker.include_router(router=router)
app = FastStream(broker)


@app.after_startup
async def setup_infrastructure():
    await setup_rabbit_infrastructure(broker)


async def main():
    setup_dishka(container=container, app=app, auto_inject=True)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
