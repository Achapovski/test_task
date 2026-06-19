from dataclasses import dataclass
from typing import Final, NamedTuple


class IntegrationConstr(NamedTuple):
    WEBHOOK_PATTERN: str = (
        r"^https:\/\/(?:[a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,}(?::\d{1,5})?(?:\/[^\s?]*)?(?:\?[^\s]*)?$"
    )


@dataclass(frozen=True)
class Constraints:
    INTEGRATION: Final[IntegrationConstr] = IntegrationConstr()
