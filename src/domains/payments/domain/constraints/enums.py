from enum import StrEnum


class PaymentStatusEnum(StrEnum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"


class CurrencyEnum(StrEnum):
    USD = "USD"
    EUR = "EUR"
