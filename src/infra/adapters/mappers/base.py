from abc import ABC
from functools import lru_cache
from operator import attrgetter
from typing import Any

from src.core.interfaces.mappers import AbstractMapper
from src.core.interfaces.models import AbstractEntity
from src.core.interfaces.storages import AbstractModelMixin


class BaseMapper[Entity: AbstractEntity, Model: AbstractModelMixin](AbstractMapper, ABC):
    """
    Базовый преобразователь между доменными сущностями и моделями БД. Обеспечивает двустороннюю конвертацию.

    :arg:entity_class: Класс доменной сущности.
    :arg model_class: Класс модели БД (Mixin/ORM).
    :arg mapping_attrs: Словарь переопределения путей атрибутов. Ключ — имя в модели, значение — путь в сущности.
    """

    entity_class = AbstractEntity
    model_class = AbstractModelMixin
    mapping_attrs: dict[str, str] = dict()

    @classmethod
    def from_entity(cls, entity: Entity) -> Model:
        """Создает новый экземпляр модели БД на основе доменной сущности."""

        return cls.model_class(**cls.to_model_dict(entity))  # type: ignore

    @classmethod
    def to_entity(cls, model: Model) -> Entity:
        """
        Создает доменную сущность из модели БД.
        Извлекает только те колонки, которые определены в модели, и передает их в конструктор сущности.
        """

        params = {attr: getattr(model, attr) for attr in tuple(model.get_columns())}
        params["metadata"] = getattr(model, "metadata_")
        return cls.entity_class(**params)

    @classmethod
    def apply_from_entity[SelfModel: "Model"](cls, entity: Entity, model: SelfModel) -> SelfModel:
        """Обновляет существующий экземпляр модели данными из сущности."""

        data = entity.as_plain()
        data.update(cls.mapping_attrs)

        for attr in data:
            if hasattr(model, attr):
                setattr(model, attr, cls._find_attr(obj=entity, data=data, attr=attr))
        return model

    @classmethod
    def to_model_dict(cls, entity: Entity) -> dict[str, Any]:
        """
        Преобразует сущность в плоский словарь, подходящий для параметров модели БД.
        Фильтрует атрибуты, оставляя только те, что заявлены в колонках модели.
        """

        data = entity.as_plain()
        data.update(cls.mapping_attrs)
        model_columns = tuple(cls.model_class.get_columns())

        return {attr: cls._find_attr(obj=entity, data=data, attr=attr) for attr in data if attr in model_columns}

    @classmethod
    def _find_attr(cls, obj: AbstractEntity, data: dict, attr: str) -> Any:
        """
        Внутренний поиск значения атрибута.
        Если атрибут переопределен в mapping_attrs, извлекает его по вложенному пути.
        """

        if attr in cls.mapping_attrs:
            attr = cls._get_attr(attr_path=cls.mapping_attrs[attr], obj_name=obj.entity_name)
            return attr(obj)
        return data[attr]

    @lru_cache(100)
    @staticmethod
    def _get_attr(attr_path: str, obj_name: str) -> Any:  # noqa: F841
        """
        Создает и кеширует оператор извлечения атрибутов (attrgetter).

        :arg attr_path: Путь к атрибуту (например, 'money.amount').
        :arg obj_name: Имя сущности (используется для разделения кеша).
        """

        return attrgetter(attr_path)
