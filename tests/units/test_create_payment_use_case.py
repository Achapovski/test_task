from decimal import Decimal
from uuid import uuid4

import pytest

from domains.payments.domain.constraints.enums import CurrencyEnum
from src.app.dto.payments import PaymentCreateRequestDTO


@pytest.mark.asyncio
async def test_should_create_payment(
    create_payment_use_case, application_payment_uow, payments_repository, outbox_repository
):
    payments_repository.get_by_idempotency_key.return_value = None

    dto = PaymentCreateRequestDTO(amount=Decimal("100.00"), currency=CurrencyEnum.USD)
    response = await create_payment_use_case.execute(idempotency_key=uuid4(), payment=dto)

    payments_repository.add.assert_awaited_once()
    outbox_repository.add_msgs.assert_awaited_once()
    application_payment_uow.commit.assert_awaited_once()

    assert response.amount == Decimal("100.00")
    assert response.currency == CurrencyEnum.USD
