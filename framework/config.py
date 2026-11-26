"""Run configuration, read from environment variables (prefix ``SAUCE_``) or a local ``.env``."""

from functools import cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SAUCE_", env_file=".env", extra="ignore")

    base_url: str = "https://www.saucedemo.com"
    # No default on purpose: a missing or empty password fails fast with a clear error.
    password: SecretStr = Field(min_length=1)
    # Response-time budget for a page to appear (tests/ui/test_performance.py). A slower
    # environment can raise it with SAUCE_PAGE_BUDGET_SECONDS, without a code change.
    page_budget_seconds: float = 2.0


@cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from env
