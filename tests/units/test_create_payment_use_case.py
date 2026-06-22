from decimal import Decimal
from uuid import uuid4

import pytest

from src.app.dto.payments import PaymentCreateRequestDTO
from src.domains.payments.domain.constraints.enums import CurrencyEnum
from src.domains.payments.exceptions import PaymentAlreadyExistsException


@pytest.mark.asyncio
async def test_should_create_payment(
    create_payment_use_case, application_payment_uow, payments_repository, outbox_repository
):
    dto = PaymentCreateRequestDTO(amount=Decimal("100.00"), currency=CurrencyEnum.USD)
    response = await create_payment_use_case.execute(idempotency_key=uuid4(), payment=dto)

    payments_repository.add.assert_awaited_once()
    outbox_repository.add_msgs.assert_awaited_once()

    assert response.amount == Decimal("100.00")
    assert response.currency == CurrencyEnum.USD


@pytest.mark.asyncio
async def test_should_return_existing_payment_when_duplicate_insert_occurs(
    create_payment_use_case, payments_uow, payments_repository, payment_factory
):
    existing_payment = payment_factory()

    payments_repository.add.side_effect = PaymentAlreadyExistsException()
    payments_repository.get_by_idempotency_key.return_value = existing_payment

    dto = PaymentCreateRequestDTO(amount=Decimal("100.00"), currency=CurrencyEnum.USD)

    response = await create_payment_use_case.execute(idempotency_key=existing_payment.idempotency_key, payment=dto)

    payments_repository.add.assert_awaited_once()
    payments_uow.rollback.assert_awaited_once()
    payments_repository.get_by_idempotency_key.assert_awaited_once()

    assert response.id == existing_payment.id


@pytest.mark.asyncio
async def test_should_return_existing_payment_after_integrity_error(
    create_payment_use_case,
    payments_repository,
    outbox_repository,
    payments_uow,
    payment_factory,
):
    existing_payment = payment_factory()

    payments_repository.add.side_effect = PaymentAlreadyExistsException()
    payments_repository.get_by_idempotency_key.return_value = existing_payment

    dto = PaymentCreateRequestDTO(amount=Decimal("100"), currency=CurrencyEnum.USD)
    result = await create_payment_use_case.execute(existing_payment.idempotency_key, dto)

    payments_uow.rollback.assert_awaited_once()
    payments_repository.get_by_idempotency_key.assert_awaited_once()

    assert result.id == existing_payment.id
