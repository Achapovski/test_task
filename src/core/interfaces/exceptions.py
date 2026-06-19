from abc import ABC, abstractmethod
from typing import Optional

from src.core.exceptions.constants import ErrorCodeEnum, ErrorLayerCode


class AbstractBaseException(ABC, Exception):
    MESSAGE: str
    DETAIL: Optional[str] = None

    _ERROR_LAYER_CODE: int = ErrorLayerCode.CORE
    _ERROR_CORRELATION: int = ErrorCodeEnum.INTERNAL_ERROR
    _ERROR_INDEX: int = 99

    def __init__(
        self, layer: Optional[ErrorLayerCode] = None, index: Optional[int] = None, correlation: Optional[int] = None
    ) -> None:
        self._ERROR_LAYER_CODE = layer or self._ERROR_LAYER_CODE
        self._ERROR_INDEX = index or self._ERROR_INDEX
        self._ERROR_CORRELATION = correlation or self._ERROR_CORRELATION

        self._ERROR_CODE = int(f"{self._ERROR_LAYER_CODE:02d}{self._ERROR_CORRELATION:02d}{self._ERROR_INDEX:02d}")

    @property
    def error_code(self) -> int:
        return self._ERROR_CODE

    @abstractmethod
    def pack(self) -> dict[str, str]:
        raise NotImplementedError()
