"""Checkout: totals (item total, tax, total), required fields, and the empty-cart bug.

Products are the first ones the page shows, and expected totals are computed from the
prices the product list showed, so a catalog change doesn't break these tests.
"""

from dataclasses import replace
from decimal import Decimal

import pytest
from playwright.sync_api import expect

from framework.bugs import xfail_bug
from framework.data.customer import CUSTOMER, Customer
from framework.money import expected_tax
from framework.pages.cart_page import CartItem, CartPage
from framework.pages.checkout_pages import (
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
)
from framework.pages.inventory_page import InventoryPage, Product
from framework.testcase import tc

pytestmark = [pytest.mark.checkout, pytest.mark.regression]

ALL_PRODUCTS = None  # slice end: [:None] takes every product


def start_checkout(
    inventory_page: InventoryPage, cart_page: CartPage, products: list[Product]
) -> None:
    """Add the products, open the cart and click Checkout."""
    for product in products:
        inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    cart_page.checkout()


@pytest.mark.happy
@pytest.mark.parametrize(
    "count",
    [
        pytest.param(1, id="one-product", marks=[tc("TC-CHECKOUT-001"), pytest.mark.smoke]),
        pytest.param(3, id="three-products", marks=tc("TC-CHECKOUT-002")),
        pytest.param(ALL_PRODUCTS, id="all-products", marks=tc("TC-CHECKOUT-003")),
    ],
)
def test_checkout_totals(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    checkout_overview_page: CheckoutOverviewPage,
    checkout_complete_page: CheckoutCompletePage,
    count: int | None,
) -> None:
    chosen = inventory_page.products()[:count]
    if count:
        assert len(chosen) == count, f"need {count} products, the page shows {len(chosen)}"

    start_checkout(inventory_page, cart_page, chosen)
    checkout_info_page.fill(CUSTOMER)
    checkout_info_page.continue_()

    subtotal = sum((p.price for p in chosen), Decimal(0))
    tax = expected_tax(subtotal)
    overview = checkout_overview_page
    assert overview.items() == [CartItem(p.name, p.price, 1) for p in chosen]
    assert overview.subtotal() == subtotal, "item total isn't the sum of the prices"
    assert overview.tax() == tax, "tax isn't 8% of the item total"
    assert overview.total() == subtotal + tax, "total isn't item total + tax"

    overview.finish()
    expect(checkout_complete_page.complete_header).to_have_text("Thank you for your order!")
    expect(checkout_complete_page.header.cart_badge).to_be_hidden()  # the cart was emptied


@pytest.mark.negative
@pytest.mark.parametrize(
    ("customer", "message"),
    [
        pytest.param(
            replace(CUSTOMER, first_name=""),
            "Error: First Name is required",
            id="no-first-name",
            marks=tc("TC-CHECKOUT-004"),
        ),
        pytest.param(
            replace(CUSTOMER, last_name=""),
            "Error: Last Name is required",
            id="no-last-name",
            marks=tc("TC-CHECKOUT-005"),
        ),
        pytest.param(
            replace(CUSTOMER, postal_code=""),
            "Error: Postal Code is required",
            id="no-postal-code",
            marks=tc("TC-CHECKOUT-006"),
        ),
        pytest.param(
            Customer("", "", ""),
            "Error: First Name is required",  # fields are checked top to bottom
            id="all-empty",
            marks=tc("TC-CHECKOUT-007"),
        ),
    ],
)
def test_checkout_validation(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_info_page: CheckoutInfoPage,
    customer: Customer,
    message: str,
) -> None:
    start_checkout(inventory_page, cart_page, inventory_page.products()[:1])
    checkout_info_page.fill(customer)
    checkout_info_page.continue_()
    expect(checkout_info_page.error).to_have_text(message)
    expect(checkout_info_page.page).to_have_url(CheckoutInfoPage.URL)  # didn't move on


@tc("TC-CHECKOUT-008")
@pytest.mark.negative
@pytest.mark.bug
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
