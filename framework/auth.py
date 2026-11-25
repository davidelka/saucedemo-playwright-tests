"""Log in once per user and save the session, so tests can start already logged in.

Playwright's *storage state* is a JSON snapshot of a browser context's cookies
and localStorage. A new context created with ``storage_state=<file>`` starts with
that session, so the test skips the login form entirely.

Sauce Demo keeps the session in a ``session-username`` cookie that expires after
10 minutes, so a saved state older than ``AUTH_STATE_MAX_AGE`` is re-created.
"""

from datetime import timedelta
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser

from framework.data.users import User
from framework.pages.inventory_page import InventoryPage
from framework.pages.login_page import LoginPage

# Half the cookie lifetime: a state is never used close to its expiry.
AUTH_STATE_MAX_AGE = timedelta(minutes=5)


def save_storage_state(
    browser: Browser, context_args: dict[str, Any], user: User, password: str, path: Path
) -> Path:
    """Log ``user`` in through the UI in a throwaway context and save its session to ``path``."""
    context = browser.new_context(**context_args)
    try:
        page = context.new_page()
        login = LoginPage(page)
        login.open()
        login.login(user, password)
        # wait_for_url uses the navigation timeout (30s), not the 5s assertion
        # timeout: performance_glitch_user takes ~5s to log in.
        page.wait_for_url(f"**{InventoryPage.PATH}")
        context.storage_state(path=path)
    finally:
        context.close()
    return path
