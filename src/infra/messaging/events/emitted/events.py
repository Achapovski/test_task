from typing import Optional
from uuid import UUID

from pydantic import AnyUrl, HttpUrl

from src.infra.messaging.events.base import BaseEvent


class PaymentCreatedEvent(BaseEvent):
    id: UUID
    webhook_url: Optional[AnyUrl]


class PaymentProcessedEvent(BaseEvent):
    id: UUID
    status: str
    webhook_url: Optional[HttpUrl]
