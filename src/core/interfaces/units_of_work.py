from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Self

from src.core.interfaces.exceptions import AbstractBaseException


class AbstractUnitOfWork(ABC):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[AbstractBaseException]],
        exc_val: Optional[AbstractBaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError()
