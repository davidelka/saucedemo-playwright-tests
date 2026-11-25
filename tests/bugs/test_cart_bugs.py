"""Known bugs when adding and removing products. See BUGS.md.

Each test runs as standard_user first: there it must pass, which proves the test
itself is right. For the buggy users it's an expected failure linked to BUGS.md.
"""

import pytest
from playwright.sync_api import expect

from framework.bugs import xfail_bug
from framework.data.users import User
from framework.pages.cart_page import CartItem, CartPage
from framework.pages.inventory_page import InventoryPage
from framework.testcase import tc

pytestmark = [pytest.mark.bug, pytest.mark.cart, pytest.mark.regression]

ADD_BUG = ("BUG-005", "Add to cart does nothing for some products")
REMOVE_BUG = ("BUG-006", "Remove on the product list does nothing")


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CART-005")),
        pytest.param(User.PROBLEM, marks=[tc("TC-CART-006"), xfail_bug(*ADD_BUG)]),
        pytest.param(User.ERROR, marks=[tc("TC-CART-007"), xfail_bug(*ADD_BUG)]),
    ],
)
def test_every_product_can_be_added(
    inventory_page: InventoryPage, cart_page: CartPage, user: User
) -> None:
    products = inventory_page.products()
    for product in products:
        inventory_page.add_to_cart(product.name)
    expect(inventory_page.header.cart_badge).to_have_text(str(len(products)))
    inventory_page.header.open_cart()
    assert cart_page.items() == [CartItem(p.name, p.price, 1) for p in products]


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CART-008")),
        pytest.param(User.PROBLEM, marks=[tc("TC-CART-009"), xfail_bug(*REMOVE_BUG)]),
        pytest.param(User.ERROR, marks=[tc("TC-CART-010"), xfail_bug(*REMOVE_BUG)]),
    ],
)
def test_product_can_be_removed_from_the_list(inventory_page: InventoryPage, user: User) -> None:
    product = inventory_page.products()[0]
    inventory_page.add_to_cart(product.name)
    expect(inventory_page.header.cart_badge).to_have_text("1")
    inventory_page.remove_from_cart(product.name)
    expect(inventory_page.header.cart_badge).to_be_hidden()
