"""The side menu behind the ☰ button in the header: About, Logout, Reset App State."""

from playwright.sync_api import Page, expect


class Menu:
    def __init__(self, page: Page) -> None:
        self.open_button = page.get_by_role("button", name="Open Menu")
        # The sliding panel (react-burger-menu). It has no data-test.
        self.panel = page.locator(".bm-menu-wrap")
        self.about_link = page.get_by_test_id("about-sidebar-link")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")
        self.reset_link = page.get_by_test_id("reset-sidebar-link")

    def is_open(self) -> bool:
        # aria-hidden tells open from closed. Visibility can't: until the late hide (see
        # open()), Playwright counts the closed, off-screen panel as visible.
        return self.panel.get_attribute("aria-hidden") == "false"

    def open(self) -> None:
        """Open the menu once the closed panel has settled, and wait until it is shown.

        If the menu is already open (Reset App State leaves it open), there is nothing to do.

        The closed panel sits off-screen, and about half a second after the page renders
        the menu also gives it the ``hidden`` attribute. In a full parallel run in Firefox,
        a click on ☰ landed before that: the trace showed the panel open
        (``aria-hidden="false"``) and ``hidden="true"`` at the same time, and Logout never
        became visible. So wait until the closed panel is hidden: by then that late hide
        has happened, and the click can't race it. (Seen under heavy load only; timed
        clicks didn't reproduce it on demand.)
        """
        if self.is_open():
            return
        expect(self.panel, "the closed side menu never settled").to_be_hidden()
        self.open_button.click()
        expect(self.panel, "the side menu didn't open").to_be_visible()  # the click took effect

    def logout(self) -> None:
        self.open()
        self.logout_link.click()

    def reset_app_state(self) -> None:
        self.open()
        self.reset_link.click()
