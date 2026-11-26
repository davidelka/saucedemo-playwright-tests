"""The side menu behind the ☰ button in the header: About, Logout, Reset App State."""

import warnings

from playwright.sync_api import Page, expect


class Menu:
    def __init__(self, page: Page) -> None:
        self.open_button = page.get_by_role("button", name="Open Menu")
        # The sliding panel. It has no data-test; it says whether it's open in aria-hidden.
        self.panel = page.locator(".bm-menu-wrap")
        self.about_link = page.get_by_test_id("about-sidebar-link")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")

    def open(self) -> None:
        """Open the menu and wait until it says it's open.

        The panel sets ``aria-hidden="false"`` as soon as it handles the click. Once, in
        Firefox under heavy parallel load, a click right after the page loaded was ignored:
        the site starts through a redirect (``/inventory.html`` -> ``/?/inventory.html``)
        and can look ready before it is. So if the menu hasn't opened after a short wait,
        click once more, and say so in the run's warnings. A second click can't close a
        menu that is just slow to slide in, because the flag changes immediately.
        """
        self.open_button.click()
        try:
            expect(self.panel).to_have_attribute("aria-hidden", "false", timeout=2_000)
        except AssertionError:
            warnings.warn("the side menu ignored a click; clicked again", stacklevel=2)
            self.open_button.click()
            expect(self.panel, "the side menu didn't open").to_have_attribute(
                "aria-hidden", "false"
            )

    def logout(self) -> None:
        self.open()
        self.logout_link.click()

    def reset_app_state(self) -> None:
        self.open()
        self.reset_link.click()
