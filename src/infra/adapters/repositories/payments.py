from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database.interfaces.repositories import SqlAlchemyAbstractRepository
from src.domains.payments.domain.entities import PaymentEntity
from src.domains.payments.exceptions import PaymentAlreadyExistsException, PaymentNotFoundException
from src.domains.payments.interfaces.repositories import PaymentsAbstractRepository
from src.infra.adapters.mappers.payments import SqlAlchemyPaymentMapper
from src.infra.adapters.models.payments import Payment


class SqlAlchemyPaymentsRepository[Entity: PaymentEntity](SqlAlchemyAbstractRepository, PaymentsAbstractRepository):
    async def add(self, entity: Entity) -> None:
        try:
            with self.session.no_autoflush:
                self.session.add(SqlAlchemyPaymentMapper.from_entity(entity=entity))
                await self.session.flush()
        except IntegrityError:
            raise PaymentAlreadyExistsException()

    async def get(self, entity_id: UUID, for_update: bool = False) -> Entity:
        stmt = select(Payment).where(Payment.id == entity_id)
        if for_update:
            stmt = stmt.with_for_update()

        if model := await self.session.scalar(stmt):
            return SqlAlchemyPaymentMapper.to_entity(model=model)
        raise PaymentNotFoundException()

    async def get_by_idempotency_key(self, idempotency_key: UUID) -> Optional[PaymentEntity]:
        if model := await self.session.scalar(select(Payment).where(Payment.idempotency_key == idempotency_key)):
            return SqlAlchemyPaymentMapper.to_entity(model=model)
        return None

    async def update(self, entity: Entity) -> None:
        if not (model := await self.session.scalar(select(Payment).where(Payment.id == entity.id))):
            raise PaymentNotFoundException()
        return SqlAlchemyPaymentMapper.apply_from_entity(entity=entity, model=model)

    async def delete(self, entity_id: UUID) -> bool:
        raise NotImplementedError()
