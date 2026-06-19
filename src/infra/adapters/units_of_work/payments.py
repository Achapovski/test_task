from src.core.database.interfaces.units_of_work import SqlAlchemyAbstractUnitOfWork
from src.core.interfaces.units_of_work import AbstractUnitOfWork
from src.domains.payments.interfaces.units_of_work import PaymentsUnitOfWork
from src.infra.adapters.repositories.outbox import SQLAlchemyOutboxRepository
from src.infra.adapters.repositories.payments import SqlAlchemyPaymentsRepository
from src.infra.outbox.interfaces import OutboxUnitOfWork


class SqlAlchemyPaymentsUnitOfWork(SqlAlchemyAbstractUnitOfWork, PaymentsUnitOfWork, OutboxUnitOfWork):
    async def __aenter__(self) -> AbstractUnitOfWork:
        uow = await super().__aenter__()
        self.outbox: SQLAlchemyOutboxRepository = SQLAlchemyOutboxRepository(session=self.session)
        self.payments: SqlAlchemyPaymentsRepository = SqlAlchemyPaymentsRepository(session=self.session)
        return uow
