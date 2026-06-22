from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.app.interfaces.units_of_work import ApplicationPaymentUnitOfWork
from src.app.use_cases.change_payment_status import ChangePaymentStatusUseCase
from src.app.use_cases.create_payment import CreatePaymentUseCase
from src.app.use_cases.get_payment import GetPaymentUseCase
from src.app.use_cases.set_payment_processed import SetPaymentProcessedUseCase
from src.infra.adapters.units_of_work.payments import SqlAlchemyPaymentsUnitOfWork


class UseCaseProvider(Provider):
    scope: Scope = Scope.REQUEST

    create_payment_use_case: CreatePaymentUseCase = provide(CreatePaymentUseCase)
    get_payment_use_case: GetPaymentUseCase = provide(GetPaymentUseCase)
    change_payment_status_uce_case: ChangePaymentStatusUseCase = provide(ChangePaymentStatusUseCase)
    set_payment_delivery_use_case: SetPaymentProcessedUseCase = provide(SetPaymentProcessedUseCase)

    @provide(scope=Scope.REQUEST)
    async def provide_app_uow(self, session_maker: async_sessionmaker) -> ApplicationPaymentUnitOfWork:
        return SqlAlchemyPaymentsUnitOfWork(session_maker=session_maker)  # type: ignore
