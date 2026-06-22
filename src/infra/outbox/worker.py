import logging

from faststream._internal.broker import BrokerUsecase  # noqa

from src.core import settings
from src.infra.outbox.interfaces import OutboxUnitOfWork

logging.basicConfig(level=settings.LOGGING.LEVEL, format=settings.LOGGING.FORMAT)
logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, uow: OutboxUnitOfWork, broker: BrokerUsecase):
        self._uow = uow
        self._broker = broker

    async def process_message(self) -> None:
        async with self._uow as uow:
            try:
                for msg in await uow.outbox.get_unpublished():
                    await self._broker.publish(message=msg.body, queue=msg.topic)
                    await uow.outbox.mark_as_published(msg)
            except Exception:
                logger.exception("Error or publishing event.")
                raise
            await uow.commit()
