from enum import StrEnum


class OutboxMessageStatusEnum(StrEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
