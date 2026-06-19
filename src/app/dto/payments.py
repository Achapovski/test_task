from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import Field

from src.app.dto.base import BaseDTO
from src.domains.payments.domain.constraints.enums import CurrencyEnum, PaymentStatusEnum


class PaymentCreateRequestDTO(BaseDTO):
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: CurrencyEnum
    description: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    webhook_url: Optional[str] = None


class PaymentCreateResponseDTO(BaseDTO):
    id: UUID
    amount: Decimal
    currency: CurrencyEnum
    status: PaymentStatusEnum
    created_at: datetime


class PaymentUpdateStatusRequestDTO(BaseDTO):
    id: UUID
    status: PaymentStatusEnum


class PaymentGetResponseDTO(BaseDTO):
    id: UUID
    idempotency_key: UUID
    amount: Decimal
    currency: str
    metadata: Optional[dict[str, Any]]
    description: Optional[str] = None
    status: PaymentStatusEnum
    webhook_url: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
