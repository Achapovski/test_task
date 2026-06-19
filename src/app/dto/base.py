from typing import Any, Literal, Optional

from pydantic import BaseModel

from src.core.interfaces.models import AbstractDTO


class BaseDTO(AbstractDTO, BaseModel):
    def as_dict(
        self,
        exclude: Optional[set] = None,
        exclude_none: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        mode: Literal["json", "python"] = "python",
    ) -> dict[str, Any]:
        return self.model_dump(
            mode=mode,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @classmethod
    def validate[CLS: BaseDTO](cls: type[CLS], obj: Any) -> CLS:
        return cls.model_validate(obj=obj, from_attributes=True)
