from types import TracebackType
from typing import Callable, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.interfaces.exceptions import AbstractBaseException
from src.core.interfaces.units_of_work import AbstractUnitOfWork


class SqlAlchemyAbstractUnitOfWork[UoW](AbstractUnitOfWork):
    def __init__(self, session_maker: Union[async_sessionmaker, Callable[..., AsyncSession]]) -> None:
        super().__init__()
        self._session_maker = session_maker

    async def __aenter__(self) -> UoW:
        self.session: AsyncSession = self._session_maker()
        return await super().__aenter__()

    async def __aexit__(
        self,
        exc_type: Optional[type[AbstractBaseException]],
        exc_val: Optional[AbstractBaseException],
        exc_tb: TracebackType,
    ) -> None:
        await super().__aexit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        self.session.expunge_all()
        await self.session.rollback()
