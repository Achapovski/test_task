from src.domains import exceptions as exc
from src.domains.payments.domain.constraints.enums import CurrencyEnum


class PaymentAlreadyExistsException(exc.DomainEntityAlreadyExistsException):
    MESSAGE: str = "Payment already exists."
    ERROR_INDEX: int = 1


class PaymentNotFoundException(exc.DomainEntityNotFoundException):
    MESSAGE: str = "Payment not found exception."
    ERROR_INDEX: int = 2


class PaymentStatusInvalidValueException(exc.DomainValidationException):
    ERROR_INDEX: int = 3

    def __init__(self, status: str) -> None:
        super().__init__(message=f"Provided status '{status}' is not a valid Payment status.")


class MoneyCurrencyInvalidValueException(exc.DomainValidationException):
    MESSAGE: str = f"Currency mismatch: expected on of {tuple(CurrencyEnum)}"
    ERROR_INDEX: int = 4


class MoneyAmountInvalidValueException(exc.DomainValidationException):
    MESSAGE: str = "Invalid money amount: value must be positive"
    ERROR_INDEX: int = 5


class MoneyCurrencyMismatchException(exc.DomainValidationException):
    ERROR_INDEX: int = 6

    def __init__(self, first_currency: str, second_currency: str) -> None:
        super().__init__(message=f"Cannot match '{first_currency}' to '{second_currency}' currency")


class PaymentWebhookInvalidValueException(exc.DomainValidationException):
    ERROR_INDEX: int = 7

    def __init__(self, url: str) -> None:
        super().__init__(message=f"The provided webhook '{url}' does not match the required format.")
