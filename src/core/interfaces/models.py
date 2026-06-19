from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, ClassVar
from uuid import UUID


class AbstractValueObject(ABC):
    """Base VO, from with any VO should be inherited."""

    @abstractmethod
    def as_plain(self) -> Any:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def validator[Func: Callable](func: Func) -> Func:
        raise NotImplementedError()


class AbstractEntity(ABC):
    """Base Entity, from which any entities should be inherited."""

    __slots__ = "_events", "_id"

    def __init__(self, id: UUID):
        self._id: UUID = id

    @property
    @abstractmethod
    def __entity_name__(self) -> str:
        raise NotImplementedError()

    @property
    def entity_name(self) -> str:
        return self.__entity_name__

    @property
    def id(self) -> UUID:
        return self._id

    @abstractmethod
    def as_plain(self) -> dict:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def create[T: "AbstractEntity"](cls: type[T], *args, **kwargs) -> T:
        raise NotImplementedError()

    if TYPE_CHECKING:
        __entity_name__: ClassVar


class AbstractDTO(ABC):
    """Base DTO, from which any DTO should be inherited."""

    @abstractmethod
    def as_dict(self) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def validate(self, obj: Any) -> dict:
        raise NotImplementedError()


class AbstractEvent(ABC):
    # Base abstract event, from which any event model should be inherited.
    event_id: UUID
    event_datetime: datetime

    @abstractmethod
    def as_dict(self) -> dict[str, Any]:
        raise NotImplementedError()
