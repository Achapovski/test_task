from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from dishka import AsyncContainer, make_async_container
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.app.entrypoints.dependencies import UseCaseProvider
from src.app.use_cases.change_payment_status import ChangePaymentStatusUseCase
from src.app.use_cases.create_payment import CreatePaymentUseCase
from src.core.database.metadata import Base
from src.core.settings import Settings, settings
from src.infra.entrypoints.dependencies import InfraProvider
from src.infra.outbox.worker import OutboxWorker
from tests.factories.payments import payment_factory as _payment_factory


@pytest.fixture
def payment_factory():
    return _payment_factory()


@pytest.fixture
def payments_repository():
    repository = MagicMock()

    repository.get = AsyncMock()
    repository.update = AsyncMock()

    repository.get_by_idempotency_key = AsyncMock()
    repository.add = AsyncMock()

    return repository


@pytest.fixture
def payments_uow(payments_repository, outbox_repository):
    uow = AsyncMock()

    uow.payments = payments_repository
    uow.outbox = outbox_repository
    uow.commit = AsyncMock()

    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    return uow


@pytest.fixture
def change_payment_status_use_case(payments_uow):
    return ChangePaymentStatusUseCase(uow=payments_uow)


@pytest.fixture
def create_payment_use_case(payments_uow):
    return CreatePaymentUseCase(uow=payments_uow)


@pytest.fixture
def outbox_repository():
    repository = MagicMock()

    repository.add_msgs = AsyncMock()
    repository.get_unpublished = AsyncMock()
    repository.mark_as_published = AsyncMock()

    return repository


@pytest.fixture
def application_payment_uow(payments_repository, outbox_repository):
    uow = MagicMock()

    uow.payments = payments_repository
    uow.outbox = outbox_repository

    uow.commit = AsyncMock()

    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    return uow


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(settings.TESTING.db_dsn)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(delete(table))
        await session.commit()


@pytest.fixture
async def container(session_factory: async_sessionmaker) -> AsyncGenerator[AsyncContainer, None]:
    ioc = make_async_container(
        UseCaseProvider(),
        InfraProvider(),
        context={async_sessionmaker: session_factory, Settings: settings},
    )
    yield ioc
    await ioc.close()


@pytest.fixture
def broker():
    broker = AsyncMock()
    broker.publish = AsyncMock()
    return broker


@pytest.fixture
def outbox_uow(outbox_repository):
    uow = AsyncMock()

    uow.outbox = outbox_repository
    uow.commit = AsyncMock()

    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)

    return uow


@pytest.fixture
def outbox_worker(outbox_uow, broker):
    return OutboxWorker(uow=outbox_uow, broker=broker)
