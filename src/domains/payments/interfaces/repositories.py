from abc import ABC
from uuid import UUID

from src.core.interfaces.repositories import AbstractRepository
from src.domains.payments.domain.entities import PaymentEntity


class PaymentsAbstractRepository(AbstractRepository[PaymentEntity], ABC):
    async def get_by_idempotency_key(self, idempotency_key: UUID) -> PaymentEntity:
        raise NotImplementedError()
