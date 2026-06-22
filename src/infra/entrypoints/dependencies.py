from typing import AsyncGenerator, AsyncIterable

from aiohttp import ClientSession, ClientTimeout
from dishka import Provider, Scope, provide
from faststream._internal.broker import BrokerUsecase
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app.interfaces.units_of_work import ApplicationPaymentUnitOfWork
from src.core.settings import Settings
from src.domains.payments.interfaces.units_of_work import PaymentsUnitOfWork
from src.infra.adapters.units_of_work.payments import SqlAlchemyPaymentsUnitOfWork
from src.infra.outbox.worker import OutboxWorker


class InfraProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def provide_db_session(self, sessionmaker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def provide_payments_uow(self, session_maker: async_sessionmaker) -> PaymentsUnitOfWork:
        return SqlAlchemyPaymentsUnitOfWork(session_maker=session_maker)

    @provide(scope=Scope.REQUEST)
    async def provide_broker(self, settings: Settings) -> BrokerUsecase:
        return RabbitBroker(url=settings.BROKER.dsn.unicode_string())

    @provide(scope=Scope.REQUEST)
    async def provide_outbox_worker(self, uow: ApplicationPaymentUnitOfWork, broker: BrokerUsecase) -> OutboxWorker:
        return OutboxWorker(uow=uow, broker=broker)

    @provide(scope=Scope.APP)
    async def provide_db_sessionmaker(self, settings: Settings) -> AsyncGenerator[async_sessionmaker, None]:
        async_engine = create_async_engine(
            url=settings.DATABASE.dsn.unicode_string(),
            echo=settings.DATABASE.IS_ECHO,
            pool_size=settings.DATABASE.POOL_SIZE,
            max_overflow=settings.DATABASE.MAX_OVERFLOW,
        )
        yield async_sessionmaker(bind=async_engine, expire_on_commit=False)
        await async_engine.dispose()

    @provide(scope=Scope.APP)
    async def get_http_session(self) -> AsyncIterable[ClientSession]:
        async with ClientSession(timeout=ClientTimeout(total=10)) as session:
            yield session
