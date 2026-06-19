from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.core.interfaces.models import AbstractEvent


class BaseEvent(AbstractEvent, BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_datetime: datetime = Field(default_factory=datetime.now)
    event_status: Optional[str] = Field(default=None)

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
