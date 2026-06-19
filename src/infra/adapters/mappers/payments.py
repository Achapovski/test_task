from src.domains.payments.domain.entities import PaymentEntity
from src.infra.adapters.mappers.base import BaseMapper
from src.infra.adapters.models.payments import Payment


class SqlAlchemyPaymentMapper(BaseMapper):
    model_class = Payment
    entity_class = PaymentEntity
    mapping_attrs = {
        "amount": "money.amount",
        "currency": "money.currency",
    }
