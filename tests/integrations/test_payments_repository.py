import pytest

from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.domains.payments.exceptions import PaymentAlreadyExistsException, PaymentNotFoundException
from src.infra.adapters.repositories.payments import SqlAlchemyPaymentsRepository


@pytest.fixture
def payments_repository(db_session):
    return SqlAlchemyPaymentsRepository(session=db_session)


@pytest.mark.asyncio
async def test_should_add_payment(payment_factory, payments_repository, db_session):
    payment = payment_factory()

    await payments_repository.add(payment)
    await db_session.commit()

    loaded = await payments_repository.get(payment.id)

    assert loaded.id == payment.id
    assert loaded.money.amount == payment.money.amount
    assert loaded.money.currency == payment.money.currency


@pytest.mark.asyncio
async def test_should_get_payment_by_idempotency_key(payment_factory, payments_repository, db_session):
    payment = payment_factory()

    await payments_repository.add(payment)
    await db_session.commit()

    loaded = await payments_repository.get_by_idempotency_key(payment.idempotency_key)

    assert loaded is not None
    assert loaded.id == payment.id


@pytest.mark.asyncio
async def test_should_update_payment_status(payment_factory, payments_repository, db_session):
    payment = payment_factory()

    await payments_repository.add(payment)
    await db_session.commit()

    payment.set_status(PaymentStatusEnum.SUCCESS)

    await payments_repository.update(payment)
    await db_session.commit()

    loaded = await payments_repository.get(payment.id)

    assert loaded.status.value == PaymentStatusEnum.SUCCESS


@pytest.mark.asyncio
async def test_should_raise_when_payment_not_found(payments_repository):
    import uuid

    with pytest.raises(PaymentNotFoundException):
        await payments_repository.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_should_raise_when_payment_already_exists(
    payment_factory,
    payments_repository,
):
    payment_1 = payment_factory()
    payment_2 = payment_factory()

    payment_2._idempotency_key = payment_1.idempotency_key

    await payments_repository.add(payment_1)

    with pytest.raises(PaymentAlreadyExistsException):
        await payments_repository.add(payment_2)
