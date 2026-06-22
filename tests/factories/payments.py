import uuid
from decimal import Decimal
from typing import Any

from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.domains.payments.domain.constraints.enums import CurrencyEnum
from src.domains.payments.domain.entities import PaymentEntity


def payment_factory():
    def factory(
        *,
        amount: Decimal = Decimal("100.00"),
        currency: CurrencyEnum = CurrencyEnum.USD,
        metadata: dict[str, Any] | None = None,
        webhook_url: str | None = "https://test.com/webhook",
        description: str = "test payment",
        status: PaymentStatusEnum = PaymentStatusEnum.PENDING,
    ) -> PaymentEntity:
        payment = PaymentEntity.create(
            amount=amount,
            currency=currency,
            metadata=metadata,
            webhook_url=webhook_url,
            description=description,
            idempotency_key=uuid.uuid4(),
        )

        if status != PaymentStatusEnum.PENDING:
            payment.set_status(status)

        return payment

    return factory
