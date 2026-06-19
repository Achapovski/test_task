from functools import lru_cache
from typing import Any, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.app.exceptions.mappers import EXCEPTIONS_MAPPER
from src.core.exceptions.constants import ErrorCodeEnum, ErrorDetails
from src.core.interfaces.exceptions import AbstractBaseException
from src.domains.base import BaseDomainException


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseDomainException)
    def handle_domain_exception(request: Request, exc: AbstractBaseException) -> JSONResponse:  # noqa: F841
        return JSONResponse(status_code=_get_http_status(exc=type(exc)), content=_get_response_schema(**exc.pack()))

    @app.exception_handler(ValidationError)
    @app.exception_handler(RequestValidationError)
    def handle_request_validation_exception(
        request: Request,  # noqa: F841
        exc: Union[RequestValidationError, ValidationError],
    ) -> JSONResponse:
        errors = []
        handle_loc = lambda data: data["loc"][1:] if isinstance(exc, RequestValidationError) else data["loc"]  # noqa: E731

        for error in exc.errors():
            field = ".".join(map(str, handle_loc(error)))
            message = error["msg"]
            errors.append(f"Field '{field}': {message}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_get_response_schema(
                message=ErrorDetails.VALIDATION_ERROR, detail=errors, error_code=ErrorCodeEnum.VALIDATION
            ),
        )

    @app.exception_handler(Exception)
    def handle_internal_exception(request: Request, exc: Exception) -> JSONResponse:  # noqa: F841
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_get_response_schema(message=ErrorDetails.SERVER_ERROR, error_code=ErrorCodeEnum.INTERNAL_ERROR),
        )


@lru_cache(len(EXCEPTIONS_MAPPER))
def _get_http_status(exc: type[Exception]) -> int:
    for cls in exc.__mro__:  # type: ignore
        if cls in EXCEPTIONS_MAPPER:
            return EXCEPTIONS_MAPPER[cls]
        if cls is BaseDomainException:
            break
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _get_response_schema(message: str, error_code: int, detail: Optional[Any] = None) -> dict[str, Any]:
    return {"message": message, "detail": detail, "error_code": error_code}
