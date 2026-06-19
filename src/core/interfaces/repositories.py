from abc import ABC, abstractmethod
from uuid import UUID

from src.core.interfaces.models import AbstractEntity
from src.core.interfaces.storages import AbstractOutboxMessage


class AbstractRepository[Entity: AbstractEntity](ABC):
    @abstractmethod
    async def add(self, entity: Entity) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get(self, entity_id: UUID, for_update: bool = False) -> Entity:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, entity: Entity) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        raise NotImplementedError()


class OutboxAbstractRepository(ABC):
    @abstractmethod
    async def add_msgs(self, *messages: AbstractOutboxMessage) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def get_unpublished(self, limit: int = 10) -> list[AbstractOutboxMessage]:
        raise NotImplementedError()

    @abstractmethod
    async def mark_as_published(self, message: AbstractOutboxMessage) -> None:
        raise NotImplementedError()
