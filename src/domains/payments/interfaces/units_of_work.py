from abc import ABC

from src.core.interfaces.units_of_work import AbstractUnitOfWork
from src.domains.payments.interfaces.repositories import PaymentsAbstractRepository


class PaymentsUnitOfWork(AbstractUnitOfWork, ABC):
    payments: PaymentsAbstractRepository
