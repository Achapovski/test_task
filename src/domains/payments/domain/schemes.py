from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, TypedDict
from uuid import UUID

from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.domains.payments.domain.constraints.enums import CurrencyEnum


class PaymentCreateSchema(TypedDict):
    amount: Decimal
    currency: CurrencyEnum
    description: str
    idempotency_key: UUID
    webhook_url: Optional[str]
    metadata: Optional[dict[str, Any]]


class PaymentBuildSchema(PaymentCreateSchema):
    id: UUID
    idempotency_key: UUID
    status: PaymentStatusEnum
    created_at: datetime
    processed_at: Optional[datetime]
