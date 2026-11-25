"""Fixtures shared by the whole suite.

pytest-playwright already provides ``playwright``, ``browser``, ``context``,
``page`` and ``new_context``; the fixtures here build on them.
"""

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

import framework.auth
from framework.config import Settings, get_settings
from framework.data.users import DEFAULT_USER, User
from framework.pages.cart_page import CartPage
from framework.pages.inventory_page import InventoryPage
from framework.pages.login_page import LoginPage

pytest_plugins = ["pytester", "framework.testcase", "framework.tagging"]


# --- configuration ---------------------------------------------------------


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:
    """Overrides pytest-base-url's fixture: relative ``page.goto("/x")`` resolves against it."""
    return settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], playwright: Playwright
) -> dict[str, Any]:
    """Options for every browser context. Also points ``get_by_test_id`` at ``data-test``,
    the attribute Sauce Demo uses (Playwright's default is ``data-testid``)."""
    playwright.selectors.set_test_id_attribute("data-test")
    return browser_context_args


# --- authentication --------------------------------------------------------


@pytest.fixture(scope="session")
def auth_state(
    browser: Browser,
    browser_context_args: dict[str, Any],
    settings: Settings,
    tmp_path_factory: pytest.TempPathFactory,
) -> Callable[[User], Path]:
    """Returns a function that gives the saved-session file for a user.

    Each user logs in through the UI at most once per AUTH_STATE_MAX_AGE, per
    browser, per xdist worker (each worker has its own tmp dir, so no two
    processes write the same file).
    """
    state_dir = tmp_path_factory.mktemp("auth")
    password = settings.password.get_secret_value()

    def state_for(user: User) -> Path:
        path = state_dir / f"{user}.json"
        max_age = framework.auth.AUTH_STATE_MAX_AGE.total_seconds()
        if not path.exists() or time.time() - path.stat().st_mtime >= max_age:
            framework.auth.save_storage_state(browser, browser_context_args, user, password, path)
        return path

    return state_for


@pytest.fixture
def user() -> User:
    """The user a test runs as. Override with ``@pytest.mark.parametrize("user", [...])``."""
    return DEFAULT_USER


@pytest.fixture
def logged_in_page(
    new_context: Callable[..., BrowserContext], auth_state: Callable[[User], Path], user: User
) -> Page:
    """A page that starts logged in as ``user``, on the inventory page."""
    context = new_context(storage_state=auth_state(user))
    page = context.new_page()
    page.goto(InventoryPage.PATH)
    return page


# --- page objects ----------------------------------------------------------


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """The login page in a fresh, logged-out context."""
    return LoginPage(page)


@pytest.fixture
def inventory_page(logged_in_page: Page) -> InventoryPage:
    """The product list, logged in as ``user``."""
    return InventoryPage(logged_in_page)


@pytest.fixture
def cart_page(logged_in_page: Page) -> CartPage:
    """The cart page object on the same logged-in page (open it via the header)."""
    return CartPage(logged_in_page)
