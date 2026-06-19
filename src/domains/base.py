from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Union
from uuid import UUID

from src.core.exceptions.constants import ErrorLayerCode
from src.core.interfaces.exceptions import AbstractBaseException
from src.core.interfaces.models import AbstractEntity, AbstractValueObject
from src.domains.utils import unwrap_model


class BaseEntity(AbstractEntity, ABC):
    """Базовый класс доменной сущности."""

    __slots__ = tuple()

    def __init__(self, id: UUID) -> None:
        """
        Метод сборки сущности. Собирает сущность из входных данных
        """

        super().__init__(id=id)

    def as_plain(self) -> dict[str, Any]:
        """
        Преобразует сущность в плоский словарь "jsonable" типов.
        Автоматически обходит __slots__ или __dict__ и разворачивает вложенные модели.

        :return Словарь с публичными атрибутами сущности.
        """

        data = {}
        attrs: Iterable = getattr(self, "__slots__", getattr(self, "__dict__", None))  # type: ignore

        for key in attrs:
            public_key = key.lstrip("_")
            if hasattr(self, public_key):
                data[public_key] = unwrap_model(getattr(self, public_key))

        return data

    def __str__(self) -> str:
        return ", ".join(f"{k}={repr(v)}" for k, v in self.as_plain().items())

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__str__()})"


@dataclass(frozen=True, slots=True)
class BaseValueObject(AbstractValueObject):
    """
    Базовый класс для Объектов-Значений (Value Objects).

    Объекты класса неизменяемы и автоматически валидируют себя при создании.
    """

    def __post_init__(self: dataclass) -> None:  # type: ignore
        """
        Запускает автоматическую валидацию после инициализации.

        Проходит по всем методам объекта и вызывает те, что помечены декоратором @validator.
        """

        for attr in self.__dir__():
            if attr.startswith("__"):
                continue

            custom_attr = getattr(self, attr)
            if callable(custom_attr) and getattr(custom_attr, "_is_validator", False) is True:
                custom_attr()

    def as_plain(self) -> Any:
        """
        Приводит объект к базовому типу Python (int, str, dict).
        Если объект состоит из одного поля — возвращает его значение.
        Если из нескольких — возвращает словарь.

        :return Упрощенное представление объекта.
        """

        args = self.__dict__ or {key: getattr(self, key) for key in self.__slots__}

        if args:
            return args.popitem()[1] if len(args) == 1 else args

        class_name = self.__class__.__name__
        raise NotImplementedError(f"'{class_name}' must implement 'as_plain' method or have a 'value' attribute.")

    @staticmethod
    def validator[Func: Callable](func: Func) -> Func:
        """
        Декоратор для пометки методов валидации внутри Value Object.
            :example
                @validator
                def check_value(self):
                    if self.value < 0: raise ValueError
        """

        func._is_validator = True
        return func

    def __eq__(self, other: AbstractValueObject) -> bool:
        """Сравнение объектов по их значению используя упрощенное представление - as_plain"""

        if self is other:
            return True

        if isinstance(self, other.__class__):
            return self.as_plain() == other.as_plain()

        return False

    def __hash__(self) -> int:
        """Хеширование на основе класса и его данных"""

        return hash((self.__class__, self.as_plain()))


class BaseDomainException(AbstractBaseException):
    """
    Базовый класс для бизнес-исключений приложения.

    :arg MESSAGE (str): Общий заголовок или код ошибки.
    :arg DETAIL (str): Детальное описание причины сбоя.
    """

    def __init__(self, message: Optional[str] = None, detail: Optional[str] = None) -> None:
        """Инициализирует исключение, позволяя переопределить стандартные сообщения."""

        self.MESSAGE = message or self.MESSAGE
        self.DETAIL = detail or self.DETAIL

        super().__init__(layer=ErrorLayerCode.DOMAIN)

    def pack(self) -> dict[str, Optional[Union[int, str]]]:
        """Собирает данные исключения в словарь."""

        return {"message": self.MESSAGE, "detail": self.DETAIL, "error_code": self.error_code}
