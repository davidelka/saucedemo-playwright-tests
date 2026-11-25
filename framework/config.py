"""Run configuration, read from environment variables (prefix ``SAUCE_``) or a local ``.env``."""

from functools import cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SAUCE_", env_file=".env", extra="ignore")

    base_url: str = "https://www.saucedemo.com"
    # No default on purpose: a missing password fails fast with a clear error.
    password: SecretStr


@cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from env
