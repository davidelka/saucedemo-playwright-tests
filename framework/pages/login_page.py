"""The login page (``/``)."""

import re

from playwright.sync_api import Page


class LoginPage:
    PATH = "/"
    # For expect(page).to_have_url(): the site's root, whatever the host. With or without
    # a trailing slash in the base URL, the browser shows the root as "https://host/".
    URL = re.compile(r"^https?://[^/]+/$")

    def __init__(self, page: Page) -> None:
        self.page = page
        # get_by_test_id reads the `data-test` attribute (configured in tests/conftest.py).
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")

    def open(self) -> None:
        self.page.goto(self.PATH)

    def fill(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)

    def submit(self) -> None:
        self.login_button.click()

    def login(self, username: str, password: str) -> None:
        self.fill(username, password)
        self.submit()
