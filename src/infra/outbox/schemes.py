from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core.interfaces.storages import AbstractOutboxMessage
from src.infra.outbox.enums import OutboxMessageStatusEnum


class OutboxMessageScheme(AbstractOutboxMessage, BaseModel):
    id: UUID = Field(default_factory=uuid4)
    body: dict[str, Any]
    topic: str
    status: OutboxMessageStatusEnum = Field(default=OutboxMessageStatusEnum.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
