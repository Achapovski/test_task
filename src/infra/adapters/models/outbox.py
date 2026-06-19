import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import UUID, VARCHAR, DateTime, Index
from sqlalchemy.dialects.postgresql import ENUM, JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.metadata import Base
from src.infra.outbox.enums import OutboxMessageStatusEnum


class OutboxMessage(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, unique=True, nullable=False)
    body: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[OutboxMessageStatusEnum] = mapped_column(
        ENUM(OutboxMessageStatusEnum, name="outbox_message_status"),
        nullable=False,
        default=OutboxMessageStatusEnum.PENDING,
    )
    topic: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("idx_outbox_status_created_at", "status", "created_at", postgresql_using="btree"),)
