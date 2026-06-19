from datetime import datetime, timezone
from typing import Any, Optional, Self, Unpack
from uuid import UUID, uuid4

from src.domains.base import BaseEntity
from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.domains.payments.domain.schemes import PaymentBuildSchema, PaymentCreateSchema
from src.domains.payments.domain.value_objects import PaymentMoney, PaymentStatus, PaymentWebhook
from src.domains.utils import typed_attrs_as_private


class PaymentEntity(BaseEntity):
    __slots__ = (*typed_attrs_as_private(PaymentBuildSchema), "_money")
    __entity_name__ = "payment"

    def __init__(self, **kwargs: Unpack[PaymentBuildSchema]) -> None:
        super().__init__(id=kwargs["id"])
        self._status = PaymentStatus(kwargs["status"])
        self._money = PaymentMoney(amount=kwargs["amount"], currency=kwargs["currency"])
        self._metadata = kwargs["metadata"]
        self._webhook_url = PaymentWebhook(kwargs["webhook_url"])
        self._idempotency_key = kwargs["idempotency_key"]
        self._description = kwargs["description"]
        self._created_at = kwargs["created_at"]
        self._processed_at = kwargs["processed_at"]

    @property
    def status(self) -> PaymentStatus:
        return self._status

    @property
    def metadata(self) -> Optional[dict[str, Any]]:
        return self._metadata

    @property
    def money(self) -> PaymentMoney:
        return self._money

    @property
    def webhook_url(self) -> PaymentWebhook:
        return self._webhook_url

    @property
    def idempotency_key(self) -> UUID:
        return self._idempotency_key

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def processed_at(self) -> Optional[datetime]:
        return self._processed_at

    def set_status(self, status: PaymentStatusEnum) -> None:
        if self._status.value not in (PaymentStatusEnum.SUCCESS, PaymentStatusEnum.FAILED):
            self._status = PaymentStatus(status)
        return None

    def delivered(self) -> None:
        if not self.processed_at:
            self._processed_at = datetime.now(tz=timezone.utc)

    @classmethod
    def create(cls, **kwargs: Unpack[PaymentCreateSchema]) -> Self:
        id_ = uuid4()
        now = datetime.now(tz=timezone.utc)

        instance = cls(id=id_, created_at=now, status=PaymentStatusEnum.PENDING, processed_at=None, **kwargs)
        return instance
