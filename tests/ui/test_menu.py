"""Side menu (☰ in the header): logout, the About link, Reset App State.

Logging out here ends only this test's browser session: every test starts from its own
copy of the saved session, so other tests stay logged in.
"""

import re

import pytest
from playwright.sync_api import expect

from framework.bugs import bug_symptom, xfail_bug
from framework.data.users import User
from framework.pages.inventory_page import InventoryPage
from framework.pages.login_page import LoginPage
from framework.testcase import tc

pytestmark = [pytest.mark.menu, pytest.mark.regression]

NOT_LOGGED_IN = "Epic sadface: You can only access '/inventory.html' when you are logged in."
ABOUT_PAGE = re.compile(r"^https://saucelabs\.com/?$")


@tc("TC-MENU-001")
@pytest.mark.login
@pytest.mark.happy
def test_logout_returns_to_login_page(inventory_page: InventoryPage) -> None:
    inventory_page.header.menu.logout()
    expect(inventory_page.page).to_have_url(LoginPage.URL)
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


@pytest.mark.bug
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-MENU-003")),
        pytest.param(
            User.PROBLEM,
            marks=[tc("TC-MENU-004"), xfail_bug("BUG-015", "the About link goes to an error page")],
        ),
    ],
)
def test_about_link_points_to_sauce_labs(inventory_page: InventoryPage, user: User) -> None:
    menu = inventory_page.header.menu
    menu.open()
    expect(menu.about_link).to_be_visible()  # the menu opened
    # Only the address is checked: the test never opens the external site.
    with bug_symptom():
        expect(menu.about_link).to_have_attribute("href", ABOUT_PAGE)


# No standard_user control: standard_user has this bug.
@pytest.mark.bug
@tc("TC-MENU-005")
@xfail_bug("BUG-016", "Reset App State leaves the products' buttons on 'Remove'")
def test_reset_app_state_empties_the_cart(inventory_page: InventoryPage) -> None:
    first, second = inventory_page.products()[:2]
    inventory_page.add_to_cart(first.name)
    inventory_page.add_to_cart(second.name)
    expect(inventory_page.header.cart_badge).to_have_text("2")  # both were added
    inventory_page.header.menu.reset_app_state()
    with bug_symptom():
        expect(inventory_page.header.cart_badge).to_be_hidden()
        expect(inventory_page.items.get_by_role("button", name="Remove")).to_have_count(0)
