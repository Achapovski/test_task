from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Iterable
from uuid import UUID

from src.core.interfaces.models import AbstractEvent


class AbstractModelMixin:
    @classmethod
    @abstractmethod
    def get_columns(cls) -> Iterable[str]:
        raise NotImplementedError()

    if TYPE_CHECKING:
        get_columns: ClassVar[Iterable[str]]


class AbstractOutboxMessage(ABC):
    id: UUID
    body: AbstractEvent
    status: str
    created_at: datetime
    topic: str
