from datetime import datetime
from types import NoneType
from typing import Any, Generator, TypedDict
from uuid import UUID

from src.core.interfaces.models import AbstractEntity, AbstractValueObject


def unwrap_model[T: Any](data: T) -> T:
    """
    Рекурсивно проходит по доменной сущности и возвращает builtin объект, содержащий атрибуты сущности,
    представленные в виде базовых типов
    """

    if isinstance(data, (list, tuple, set, frozenset)):
        return [unwrap_model(obj) for obj in data]

    if isinstance(data, dict):
        return {key: unwrap_model(value) for key, value in data.items()}

    if isinstance(data, (AbstractEntity, AbstractValueObject)):
        return unwrap_model(data.as_plain())

    if isinstance(data, (str, int, float, bool, datetime, NoneType, UUID)):
        return data
    return str(data)


def typed_attrs_as_private[K, V](attrs: type[TypedDict[K, V]]) -> Generator[K, None, None]:
    """Принимает TypedDict и возвращает генератор приватных имен для полей"""

    return (attr if attr.startswith("_") else f"_{attr}" for attr in attrs.__annotations__.keys())
