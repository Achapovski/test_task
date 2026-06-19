from typing import Generator

from sqlalchemy.orm import DeclarativeBase

from src.core.interfaces.storages import AbstractModelMixin


class Base(DeclarativeBase, AbstractModelMixin):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        db_columns = tuple(self.get_columns())

        for key, value in kwargs.items():
            if key in db_columns:
                setattr(self, key, value)

    @classmethod
    def get_columns(cls) -> Generator[str, None, None]:
        return (column for column in cls.__table__.columns.keys())
