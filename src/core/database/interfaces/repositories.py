from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyAbstractRepository(ABC):
    def __init__(self, session: AsyncSession, *args, **kwargs) -> None:
        self.session: AsyncSession = session
        super().__init__(*args, **kwargs)
