"""Login: success, invalid credentials, locked-out user, empty fields, and access without login.

These tests log in through the UI on purpose. Every other test starts already
logged in from a saved session (see the ``logged_in_page`` fixture).
"""

import pytest
from playwright.sync_api import Page, expect

from framework.config import Settings
from framework.data.users import User
from framework.pages.inventory_page import InventoryPage
from framework.pages.login_page import LoginPage
from framework.testcase import tc

pytestmark = [pytest.mark.login, pytest.mark.regression]

NO_MATCH = "Epic sadface: Username and password do not match any user in this service"
USE_REAL_PASSWORD = None  # sentinel: take the password from settings


@tc("TC-LOGIN-001")
@pytest.mark.smoke
@pytest.mark.happy
def test_login_success(login_page: LoginPage, settings: Settings, page: Page) -> None:
    login_page.open()
    login_page.login(User.STANDARD, settings.password.get_secret_value())
    expect(page).to_have_url(InventoryPage.URL)
    expect(InventoryPage(page).title).to_have_text("Products")


@pytest.mark.negative
@pytest.mark.parametrize(
    ("username", "password", "message"),
    [
        pytest.param(
            User.STANDARD, "wrong", NO_MATCH, id="invalid-password", marks=tc("TC-LOGIN-002")
        ),
        pytest.param(
            "nobody", USE_REAL_PASSWORD, NO_MATCH, id="unknown-user", marks=tc("TC-LOGIN-003")
        ),
        pytest.param(
            User.LOCKED_OUT,
            USE_REAL_PASSWORD,
            "Epic sadface: Sorry, this user has been locked out.",
            id="locked-out",
            # The user here is the username parameter, not the user fixture the
            # automatic user tags read, so the tag is set by hand.
            marks=[tc("TC-LOGIN-004"), pytest.mark.user_locked_out],
        ),
        pytest.param(
            "",
            USE_REAL_PASSWORD,
            "Epic sadface: Username is required",
            id="empty-username",
            marks=tc("TC-LOGIN-005"),
        ),
        pytest.param(
            User.STANDARD,
            "",
            "Epic sadface: Password is required",
            id="empty-password",
            marks=tc("TC-LOGIN-006"),
        ),
    ],
)
def test_login_failure(
    login_page: LoginPage,
    settings: Settings,
    page: Page,
    username: str,
    password: str | None,
    message: str,
) -> None:
    login_page.open()
    login_page.login(
        username, settings.password.get_secret_value() if password is None else password
    )
    expect(login_page.error).to_have_text(message)
    expect(page).to_have_url(settings.base_url + "/")  # still on the login page


@tc("TC-LOGIN-007")
@pytest.mark.negative
def test_inventory_requires_login(page: Page) -> None:
    page.goto(InventoryPage.PATH)
    expect(LoginPage(page).error).to_have_text(
        "Epic sadface: You can only access '/inventory.html' when you are logged in."
    )
    expect(LoginPage(page).login_button).to_be_visible()
