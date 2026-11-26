"""Side menu (☰ in the header): logout, the About link, Reset App State.

Logging out here ends only this test's browser session: every test starts from its own
copy of the saved session, so other tests stay logged in.
"""

import pytest
from playwright.sync_api import expect

from framework.config import Settings
from framework.pages.inventory_page import InventoryPage
from framework.pages.login_page import LoginPage
from framework.testcase import tc

pytestmark = [pytest.mark.menu, pytest.mark.regression]

NOT_LOGGED_IN = "Epic sadface: You can only access '/inventory.html' when you are logged in."


@tc("TC-MENU-001")
@pytest.mark.login
@pytest.mark.happy
def test_logout_returns_to_login_page(inventory_page: InventoryPage, settings: Settings) -> None:
    inventory_page.header.menu.logout()
    expect(inventory_page.page).to_have_url(settings.base_url + "/")
    expect(LoginPage(inventory_page.page).login_button).to_be_visible()


@tc("TC-MENU-002")
@pytest.mark.login
@pytest.mark.negative
def test_logged_out_user_cannot_open_inventory(inventory_page: InventoryPage) -> None:
    login_page = LoginPage(inventory_page.page)
    inventory_page.header.menu.logout()
    expect(login_page.login_button).to_be_visible()  # logged out
    inventory_page.open()
    expect(login_page.error).to_have_text(NOT_LOGGED_IN)
    expect(inventory_page.title).to_be_hidden()
