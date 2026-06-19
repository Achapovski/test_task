from dataclasses import dataclass
from uuid import UUID

from src.app.dto.payments import PaymentGetResponseDTO
from src.domains.payments.interfaces.units_of_work import PaymentsUnitOfWork


@dataclass(frozen=True, slots=True)
class GetPaymentUseCase:
    uow: PaymentsUnitOfWork

    async def execute(self, payment_id: UUID) -> PaymentGetResponseDTO:
        async with self.uow as uow:
            entity = await uow.payments.get(payment_id)

        return PaymentGetResponseDTO(amount=entity.money.amount, currency=entity.money.currency, **entity.as_plain())
