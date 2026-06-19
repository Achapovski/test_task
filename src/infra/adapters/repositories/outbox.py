from datetime import datetime, timezone

from sqlalchemy import ScalarResult, insert, select

from src.core.database.interfaces.repositories import SqlAlchemyAbstractRepository
from src.core.interfaces.repositories import OutboxAbstractRepository
from src.infra.adapters.models.outbox import OutboxMessage
from src.infra.outbox.enums import OutboxMessageStatusEnum
from src.infra.outbox.schemes import OutboxMessageScheme


class SQLAlchemyOutboxRepository(SqlAlchemyAbstractRepository, OutboxAbstractRepository):
    async def add_msgs(self, *messages: OutboxMessageScheme) -> None:
        if not (data := [msg.model_dump() for msg in messages]):
            raise ValueError("Invalid outbox process")
        await self.session.execute(insert(OutboxMessage).values(*data))

    async def get_unpublished(self, limit: int = 10) -> list[OutboxMessage]:
        messages: ScalarResult[OutboxMessage] = await self.session.scalars(
            select(OutboxMessage)
            .where(OutboxMessage.status == OutboxMessageStatusEnum.PENDING)
            .limit(limit)
            .order_by(OutboxMessage.created_at)
            .with_for_update(skip_locked=True)
        )
        return list(messages.all())

    async def mark_as_published(self, message: OutboxMessage) -> None:
        message.status = OutboxMessageStatusEnum.SUCCESS
        message.published_at = datetime.now(tz=timezone.utc)
        self.session.add(message)
