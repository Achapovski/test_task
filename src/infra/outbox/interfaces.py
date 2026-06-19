from abc import ABC

from src.core.interfaces.repositories import OutboxAbstractRepository
from src.core.interfaces.units_of_work import AbstractUnitOfWork


class OutboxUnitOfWork(AbstractUnitOfWork, ABC):
    outbox: OutboxAbstractRepository
