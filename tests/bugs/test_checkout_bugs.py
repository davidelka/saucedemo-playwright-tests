"""Known bugs at checkout. See BUGS.md.

Tests that run as several users run as standard_user first: there they must pass,
which proves the test itself is right. BUG-001 affects standard_user itself.
"""

import pytest
from playwright.sync_api import expect

from framework.bugs import xfail_bug
from framework.data.customer import CUSTOMER
from framework.data.users import User
from framework.flows import start_checkout
from framework.pages.cart_page import CartPage
from framework.pages.checkout_pages import (
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
)
from framework.pages.inventory_page import InventoryPage
from framework.testcase import tc

pytestmark = [pytest.mark.bug, pytest.mark.checkout, pytest.mark.regression]


@tc("TC-CHECKOUT-008")
@pytest.mark.negative
@xfail_bug("BUG-001", "checkout is allowed with an empty cart")
def test_empty_cart_cannot_be_checked_out(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    inventory_page.header.open_cart()
    assert cart_page.items() == [], "precondition: the cart starts empty"
    # Either fix is fine: Checkout disabled, or clicking it keeps you on the cart.
    if cart_page.checkout_button.is_enabled():
        cart_page.checkout()
    expect(cart_page.page).to_have_url(CartPage.URL)


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CHECKOUT-009")),
        pytest.param(
            User.PROBLEM,
            marks=[
                tc("TC-CHECKOUT-010"),
                xfail_bug("BUG-007", "typing the last name overwrites the first name"),
            ],
        ),
        pytest.param(
            User.ERROR,
            marks=[
                tc("TC-CHECKOUT-011"),
                xfail_bug("BUG-009", "the Last Name field ignores typing"),
            ],
        ),
    ],
)
def test_checkout_fields_keep_what_you_type(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    user: User,
) -> None:
    start_checkout(inventory_page, cart_page, inventory_page.products()[:1])
    checkout_info_page.fill(CUSTOMER)
    expect(checkout_info_page.first_name).to_have_value(CUSTOMER.first_name)
    expect(checkout_info_page.last_name).to_have_value(CUSTOMER.last_name)
    expect(checkout_info_page.postal_code).to_have_value(CUSTOMER.postal_code)


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CHECKOUT-012")),
        pytest.param(
            User.ERROR,
            marks=[
                tc("TC-CHECKOUT-013"),
                xfail_bug("BUG-010", "Finish doesn't complete the order"),
            ],
        ),
    ],
)
def test_finish_completes_the_order(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    checkout_overview_page: CheckoutOverviewPage,
    checkout_complete_page: CheckoutCompletePage,
    user: User,
) -> None:
    start_checkout(inventory_page, cart_page, inventory_page.products()[:1])
    checkout_info_page.fill(CUSTOMER)
    checkout_info_page.continue_()
    expect(checkout_overview_page.finish_button).to_be_visible()  # reached the overview
    checkout_overview_page.finish()
    expect(checkout_complete_page.complete_header).to_have_text("Thank you for your order!")
