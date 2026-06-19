from enum import IntEnum, StrEnum


class ErrorDetails(StrEnum):
    """Содержит базовые сообщения об ошибках"""

    SERVER_ERROR = "Internal server error."
    BAD_REQUEST = "Bad request."
    NOT_FOUND = "Entity not found"
    VALIDATION_ERROR = "Validation error."


class ErrorLayerCode(IntEnum):
    """Содержит коды слоев приложения"""

    CORE = 99
    DOMAIN = 10


class ErrorCodeEnum(IntEnum):
    """Содержит коды основных ошибок"""

    # Ошибки входных данных
    VALIDATION = 40
    INVALID_STATE = 42
    MISSING_DATA = 43

    # Проблемы с доступом
    AUTH_REQUIRED = 41
    PERMISSION_DENIED = 45
    ACCOUNT_INACTIVE = 46
    NOT_FOUND = 44
    RELATED_NOT_FOUND = 47

    # Конфликты
    ALREADY_EXISTS = 49
    ALREADY_ATTACHED = 48

    # Системные ошибки
    INTERNAL_ERROR = 50
    SERVICE_UNAVAILABLE = 53
    LIMIT_EXCEEDED = 55
