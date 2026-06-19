import pytest

from app.dto.payments import PaymentUpdateStatusRequestDTO
from domains.payments.domain.constraints import PaymentStatusEnum


@pytest.mark.asyncio
async def test_should_change_pending_payment_status(
    payment_factory, payments_repository, payments_uow, change_payment_status_use_case
):
    payment = payment_factory()
    payments_repository.get.return_value = payment

    dto = PaymentUpdateStatusRequestDTO(id=payment.id, status=PaymentStatusEnum.SUCCESS)

    await change_payment_status_use_case.execute(dto)
    assert payment.status.value == PaymentStatusEnum.SUCCESS

    payments_repository.update.assert_awaited_once_with(payment)
    payments_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_should_not_change_processed_payment(
    payment_factory, payments_repository, payments_uow, change_payment_status_use_case
):
    payment = payment_factory()
    payment.set_status(PaymentStatusEnum.SUCCESS)
    payments_repository.get.return_value = payment
    dto = PaymentUpdateStatusRequestDTO(id=payment.id, status=PaymentStatusEnum.FAILED)

    await change_payment_status_use_case.execute(dto)

    assert payment.status.value == PaymentStatusEnum.SUCCESS

    payments_repository.update.assert_not_awaited()
    payments_uow.commit.assert_not_awaited()
