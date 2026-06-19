from fastapi import status

from src.domains.exceptions import (
    DomainEntityAlreadyExistsException,
    DomainEntityNotFoundException,
    DomainValidationException,
)

EXCEPTIONS_MAPPER = {
    DomainEntityAlreadyExistsException: status.HTTP_409_CONFLICT,
    DomainEntityNotFoundException: status.HTTP_404_NOT_FOUND,
    DomainValidationException: status.HTTP_400_BAD_REQUEST,
}
