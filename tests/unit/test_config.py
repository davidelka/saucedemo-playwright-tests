import pytest
from pydantic import ValidationError

from framework.config import Settings
from framework.testcase import tc

pytestmark = pytest.mark.unit


@tc("TC-CFG-001")
@pytest.mark.parametrize(
    "password",
    [
        None,
        # A fork's CI run gets an empty secret: without this check every login would
        # time out after 30 s instead of failing here at once.
        "",
    ],
    ids=["missing", "empty"],
)
def test_settings_require_password(monkeypatch: pytest.MonkeyPatch, password: str | None) -> None:
    if password is None:
        monkeypatch.delenv("SAUCE_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("SAUCE_PASSWORD", password)
    with pytest.raises(ValidationError, match="password"):
        Settings(_env_file=None)  # type: ignore[call-arg]


@tc("TC-CFG-002")
def test_settings_read_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SAUCE_PASSWORD", "x")
    monkeypatch.setenv("SAUCE_BASE_URL", "https://example.test")
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.password.get_secret_value() == "x"
    assert settings.base_url == "https://example.test"
