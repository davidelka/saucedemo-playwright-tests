"""The login page (``/``)."""

from playwright.sync_api import Page


class LoginPage:
    PATH = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        # get_by_test_id reads the `data-test` attribute (configured in tests/conftest.py).
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")

    def open(self) -> None:
        self.page.goto(self.PATH)

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()
