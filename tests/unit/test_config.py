import pytest
from pydantic import ValidationError

from framework.config import Settings

pytestmark = pytest.mark.unit


def test_settings_require_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SAUCE_PASSWORD", raising=False)
    with pytest.raises(ValidationError, match="password"):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_settings_read_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SAUCE_PASSWORD", "x")
    monkeypatch.setenv("SAUCE_BASE_URL", "https://example.test")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.password.get_secret_value() == "x"
    assert settings.base_url == "https://example.test"
