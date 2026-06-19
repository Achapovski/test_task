from dataclasses import dataclass
from uuid import UUID

from src.domains.payments.interfaces.units_of_work import PaymentsUnitOfWork


@dataclass(frozen=True, slots=True)
class SetPaymentDeliveryUseCase:
    uow: PaymentsUnitOfWork

    async def execute(self, payment_id: UUID) -> None:
        async with self.uow as uow:
            entity = await uow.payments.get(entity_id=payment_id, for_update=True)
            entity.delivered()

            await uow.payments.update(entity)
            await uow.commit()
