import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from dishka import AsyncContainer

from src.app.dto.payments import PaymentCreateRequestDTO
from src.app.use_cases.create_payment import CreatePaymentUseCase
from src.domains.payments.domain.constraints.enums import CurrencyEnum


@pytest.mark.asyncio
async def test_create_payment_is_idempotent_under_many_concurrent_requests(container: AsyncContainer) -> None:
    idempotency_key = uuid4()
    dto = PaymentCreateRequestDTO(amount=Decimal("1000"), currency=CurrencyEnum.USD, webhook_url=None)

    async def create():
        async with container() as scope:
            use_case = await scope.get(CreatePaymentUseCase)
            return await use_case.execute(idempotency_key=idempotency_key, payment=dto)

    results = await asyncio.gather(*(create() for _ in range(1)))

    ids = {result.id for result in results}

    assert len(ids) == 1
