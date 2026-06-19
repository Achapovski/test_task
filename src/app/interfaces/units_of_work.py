from abc import ABC

from src.core.interfaces.repositories import OutboxAbstractRepository
from src.domains.payments.interfaces.units_of_work import PaymentsUnitOfWork
from src.infra.outbox.interfaces import OutboxUnitOfWork


class ApplicationPaymentUnitOfWork(PaymentsUnitOfWork, OutboxUnitOfWork, ABC):
    outbox: OutboxAbstractRepository
