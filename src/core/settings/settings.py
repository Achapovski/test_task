import os
from functools import lru_cache

from yaml import safe_load

from src.core.settings.paths import APP_ROOT
from src.core.settings.schemes import Settings


@lru_cache(maxsize=1)
def get_settings(file: str = APP_ROOT / os.getenv("CONFIG_FILE", "config.yml")) -> Settings:
    with open(file=file, mode="r", encoding="utf-8") as file:
        return Settings.model_validate(safe_load(file))


settings = get_settings()
