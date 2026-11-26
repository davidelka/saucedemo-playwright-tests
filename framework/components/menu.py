"""The side menu behind the ☰ button in the header: About, Logout, Reset App State."""

from playwright.sync_api import Page


class Menu:
    def __init__(self, page: Page) -> None:
        self.open_button = page.get_by_role("button", name="Open Menu")
        self.about_link = page.get_by_test_id("about-sidebar-link")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")

    def open(self) -> None:
        # The menu slides in; clicks on its links wait until it has stopped moving.
        self.open_button.click()

    def logout(self) -> None:
        self.open()
        self.logout_link.click()

    def reset_app_state(self) -> None:
        self.open()
        self.reset_link.click()
