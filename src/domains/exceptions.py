from src.core.exceptions.constants import ErrorCodeEnum
from src.domains.base import BaseDomainException


class DomainEntityNotFoundException(BaseDomainException):
    """
    Выбрасывается, когда запрашиваемая сущность не найдена в системе.
    """

    MESSAGE = "Entity not found."
    ERROR_INDEX = ErrorCodeEnum.NOT_FOUND


class DomainEntityAlreadyExistsException(BaseDomainException):
    """Выбрасывается при нарушении уникальности."""

    MESSAGE = "Entity already exists."
    ERROR_INDEX = ErrorCodeEnum.ALREADY_EXISTS


class DomainValidationException(BaseDomainException):
    """Выбрасывается, когда данные не проходят проверку инвариантов."""

    MESSAGE = "Invalid data provided."
    ERROR_INDEX = ErrorCodeEnum.VALIDATION
