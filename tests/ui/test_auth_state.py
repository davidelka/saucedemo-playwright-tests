"""The saved-session login (storage state) that every non-login test starts from."""

from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

import framework.auth
from framework.data.users import User
from framework.pages.inventory_page import InventoryPage
from framework.testcase import tc

pytestmark = [pytest.mark.login, pytest.mark.regression]


@pytest.mark.happy
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=[tc("TC-AUTH-001"), pytest.mark.smoke]),
        pytest.param(User.PROBLEM, marks=tc("TC-AUTH-002")),
        pytest.param(User.PERFORMANCE_GLITCH, marks=tc("TC-AUTH-003")),
        pytest.param(User.ERROR, marks=tc("TC-AUTH-004")),
        pytest.param(User.VISUAL, marks=tc("TC-AUTH-005")),
    ],
)
def test_saved_session_opens_inventory(logged_in_page: Page, user: User) -> None:
    expect(logged_in_page).to_have_url(InventoryPage.URL)
    expect(InventoryPage(logged_in_page).title).to_have_text("Products")


@tc("TC-AUTH-006")
def test_auth_state_refreshes_when_stale(
    auth_state: Callable[[User], Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    first = auth_state(User.STANDARD).stat().st_mtime_ns
    monkeypatch.setattr(framework.auth, "AUTH_STATE_MAX_AGE", timedelta(0))
    second = auth_state(User.STANDARD).stat().st_mtime_ns
    assert second > first
