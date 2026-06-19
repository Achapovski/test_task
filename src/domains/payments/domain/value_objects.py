import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from src.domains.base import BaseValueObject
from src.domains.payments import exceptions
from src.domains.payments.domain.constraints import PaymentStatusEnum
from src.domains.payments.domain.constraints.constraints import Constraints
from src.domains.payments.domain.constraints.enums import CurrencyEnum


@dataclass(frozen=True, slots=True)
class PaymentMoney(BaseValueObject):
    amount: Decimal
    currency: CurrencyEnum

    @BaseValueObject.validator
    def validate_value(self) -> None:
        if self.currency not in CurrencyEnum:
            raise exceptions.MoneyCurrencyInvalidValueException()
        if not isinstance(self.amount, Decimal) or self.amount < 0 or not self.amount.is_finite():
            raise exceptions.MoneyAmountInvalidValueException()

    def __add__(self, other: "PaymentMoney") -> "PaymentMoney":
        self._is_valid_money(other)
        return PaymentMoney(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "PaymentMoney") -> "PaymentMoney":
        self._is_valid_money(other)
        return PaymentMoney(amount=self.amount - other.amount, currency=self.currency)

    def _is_valid_money(self, other: "PaymentMoney") -> None:
        if not isinstance(other, self.__class__):
            raise ValueError(f"Money can only be added to Money, not '{type(other).__name__}'")
        if other.currency != self.currency:
            raise exceptions.MoneyCurrencyMismatchException(
                first_currency=self.currency, second_currency=other.currency
            )


@dataclass(frozen=True, slots=True)
class PaymentStatus(BaseValueObject):
    value: str

    @BaseValueObject.validator
    def validate_value(self) -> None:
        if self.value not in PaymentStatusEnum:
            raise exceptions.PaymentStatusInvalidValueException(status=self.value)


@dataclass(frozen=True, slots=True)
class PaymentWebhook(BaseValueObject):
    value: Optional[str]

    @BaseValueObject.validator
    def validate_value(self) -> None:
        Constr = Constraints.INTEGRATION

        if not self.value:
            return None

        if not isinstance(self.value, str) or not re.match(string=self.value, pattern=Constr.WEBHOOK_PATTERN):
            raise exceptions.PaymentWebhookInvalidValueException(url=self.value)

        return None
