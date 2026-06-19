from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from src.core.interfaces.models import AbstractEntity
from src.core.interfaces.storages import AbstractModelMixin


class AbstractMapper[Entity: AbstractEntity, Model: AbstractModelMixin](ABC):
    @property
    @abstractmethod
    def model_class(self) -> type[AbstractModelMixin]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def entity_class(self) -> type[AbstractEntity]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def mapping_attrs(self) -> dict[str, str]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def to_entity(cls, model: Model) -> Entity:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_entity(cls, entity: Entity) -> Model:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def apply_from_entity[SelfModel: AbstractModelMixin](cls, entity: Entity, model: SelfModel) -> SelfModel:
        raise NotImplementedError()

    if TYPE_CHECKING:
        entity_class: ClassVar[AbstractEntity]
        model_class: ClassVar[AbstractModelMixin]
