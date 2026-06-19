import asyncio
import logging

from faststream._internal.broker import BrokerUsecase

from src.containers import container
from src.core import settings
from src.infra.outbox.worker import OutboxWorker

logging.basicConfig(level=settings.LOGGING.LEVEL, format=settings.LOGGING.FORMAT)
logger = logging.getLogger(__name__)


async def run_worker():
    async with container() as ioc:
        worker = await ioc.get(OutboxWorker)
        broker = await ioc.get(BrokerUsecase)
        try:
            await broker.start()
            while True:
                await worker.process_message()  # noqa
                await asyncio.sleep(1)
        finally:
            await broker.stop()
            logger.error("Loop was stopped")


async def main():
    logger.info("Launch worker")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_worker())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
