from dataclasses import dataclass

from src.app.dto.payments import PaymentUpdateStatusRequestDTO
from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.domains.payments.interfaces.units_of_work import PaymentsUnitOfWork


@dataclass(frozen=True, slots=True)
class ChangePaymentStatusUseCase:
    uow: PaymentsUnitOfWork

    async def execute(self, payment: PaymentUpdateStatusRequestDTO) -> None:
        async with self.uow as uow:
            entity = await uow.payments.get(entity_id=payment.id)

            if entity.status.as_plain() != PaymentStatusEnum.PENDING:
                return None

            entity.set_status(payment.status)

            await uow.payments.update(entity)
            await uow.commit()
