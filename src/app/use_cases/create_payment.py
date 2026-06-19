from dataclasses import dataclass
from uuid import UUID

from src.app.dto.payments import PaymentCreateRequestDTO, PaymentCreateResponseDTO
from src.app.interfaces.units_of_work import ApplicationPaymentUnitOfWork
from src.core import settings
from src.domains.payments.domain.entities import PaymentEntity
from src.infra.messaging.events.emitted.events import PaymentCreatedEvent
from src.infra.outbox.schemes import OutboxMessageScheme


@dataclass(frozen=True, slots=True)
class CreatePaymentUseCase:
    uow: ApplicationPaymentUnitOfWork

    async def execute(self, idempotency_key: UUID, payment: PaymentCreateRequestDTO) -> PaymentCreateResponseDTO:
        async with self.uow as uow:
            entity = await uow.payments.get_by_idempotency_key(idempotency_key)

            if not entity:
                entity = PaymentEntity.create(idempotency_key=idempotency_key, **payment.as_dict())
                await uow.payments.add(entity)
                await uow.outbox.add_msgs(self._get_outbox_msg(entity))
                await uow.commit()

        return PaymentCreateResponseDTO(amount=entity.money.amount, currency=entity.money.currency, **entity.as_plain())

    @staticmethod
    def _get_outbox_msg(entity: PaymentEntity) -> OutboxMessageScheme:
        return OutboxMessageScheme(
            body=PaymentCreatedEvent.model_validate(entity.as_plain()).as_dict(),
            topic=settings.MESSAGING.PAYMENTS.TOPICS.NEW,
        )
