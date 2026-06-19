import os
from functools import cached_property

from pydantic import AnyUrl, BaseModel, Field, PostgresDsn, SecretStr
from pydantic import networks as nts
from pydantic_settings import BaseSettings

from src.core.settings.paths import APP_ROOT


class BaseSettingsMixin:
    model_config = {
        "extra": "ignore",
        "env_file": str(APP_ROOT / os.getenv("ENV_FILE", ".env")),
    }


class DatabaseSettings(BaseSettings, BaseSettingsMixin):
    DRIVER: str
    HOST: str
    DATABASE: str
    PORT: int = Field(ge=1000, le=16394)
    USER: SecretStr
    PASSWORD: SecretStr
    IS_ECHO: bool
    POOL_SIZE: int = Field(default=5)
    MAX_OVERFLOW: int = Field(default=10)

    @cached_property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn(
            f"{self.DRIVER}://"
            f"{self.USER.get_secret_value()}:{self.PASSWORD.get_secret_value()}@{self.HOST}/{self.DATABASE}",
        )

    model_config = {"env_prefix": "DATABASE_"}


class BrokerSettings(BaseSettings, BaseSettingsMixin):
    PROTOCOL: str = Field(default="amqp")
    USER: SecretStr = Field(default="guest")
    PASSWORD: SecretStr = Field(default="guest")
    HOST: str = Field(default="localhost")
    PORT: int = Field(default=5672)

    @cached_property
    def dsn(self) -> AnyUrl:
        return self._broker_dsn(
            f"{self.PROTOCOL}://"
            f"{self.USER.get_secret_value()}:{self.PASSWORD.get_secret_value()}@"
            f"{self.HOST}:{self.PORT}"
        )

    @property
    def _broker_dsn(self) -> type[AnyUrl]:
        dsns: tuple[type[AnyUrl], ...] = (nts.AmqpDsn, nts.RedisDsn, nts.KafkaDsn, nts.NatsDsn)  # type: ignore
        for dsn in dsns:
            if self.PROTOCOL in dsn._constraints.allowed_schemes:  # noqa:
                return dsn

        allowed_protocols = chain.from_iterable((dsn._constraints.allowed_schemes for dsn in dsns))  # noqa
        raise TypeError(
            f"Unexpected broker protocol. You can use only one of '{list(allowed_protocols)}', got '{self.PROTOCOL}'."
        )

    model_config = {"env_prefix": "BROKER_"}


class ApiSettings(BaseSettings, BaseSettingsMixin):
    KEY: SecretStr

    model_config = {"env_prefix": "API_"}


class RetryLevel(BaseModel):
    TIME: int
    RKEY: str


class RetryPolicy(BaseModel):
    FIRST: RetryLevel
    SECOND: RetryLevel
    THIRD: RetryLevel


class PaymentsTopics(BaseModel):
    NEW: str
    WEBHOOKS: str
    WEBHOOKS_DEAD: str


class Payments(BaseModel):
    TOPICS: PaymentsTopics
    RETRY_POLICY: RetryPolicy


class MessagingSettings(BaseModel):
    PAYMENTS: Payments


class LoggingSettings(BaseSettings):
    FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LEVEL: str = Field(default="INFO")


class TestingSettings(BaseSettings, BaseSettingsMixin):
    DB_URL: AnyUrl

    @cached_property
    def db_dsn(self) -> str:
        return self.DB_URL.unicode_string()


class Settings(BaseModel):
    DATABASE: DatabaseSettings
    BROKER: BrokerSettings
    MESSAGING: MessagingSettings
    LOGGING: LoggingSettings
    TESTING: TestingSettings
    API: ApiSettings = ApiSettings()
