"""Cart: badge count, cart contents (names, prices, quantities), removing items.

Tests pick the first products the page shows rather than naming them, and expect the
price the product list showed. So they test that the cart shows what you added, at
the price you saw, and keep working if the catalog changes.
"""

import pytest
from playwright.sync_api import expect

from framework.pages.cart_page import CartItem, CartPage
from framework.pages.inventory_page import InventoryPage, Product
from framework.testcase import tc

pytestmark = [pytest.mark.cart, pytest.mark.regression]


def line(product: Product) -> CartItem:
    """The cart line expected for one unit of a product, at its listed price."""
    return CartItem(product.name, product.price, 1)


@tc("TC-CART-001")
@pytest.mark.smoke
@pytest.mark.happy
def test_add_products_updates_badge_and_cart(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    first, second = inventory_page.products()[:2]
    inventory_page.add_to_cart(first.name)
    inventory_page.add_to_cart(second.name)
    expect(inventory_page.header.cart_badge).to_have_text("2")

    inventory_page.header.open_cart()
    assert cart_page.items() == [line(first), line(second)]


@tc("TC-CART-002")
@pytest.mark.happy
def test_remove_from_inventory_updates_badge(inventory_page: InventoryPage) -> None:
    first, second = inventory_page.products()[:2]
    inventory_page.add_to_cart(first.name)
    inventory_page.add_to_cart(second.name)
    inventory_page.remove_from_cart(first.name)
    expect(inventory_page.header.cart_badge).to_have_text("1")


@tc("TC-CART-003")
@pytest.mark.negative
def test_remove_last_item_empties_cart(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    product = inventory_page.products()[0]
    inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    cart_page.remove(product.name)
    expect(cart_page.header.cart_badge).to_be_hidden()
    assert cart_page.items() == []


@tc("TC-CART-004")
@pytest.mark.happy
def test_cart_persists_across_navigation(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    product = inventory_page.products()[0]
    inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    cart_page.continue_shopping()
    expect(inventory_page.title).to_have_text("Products")
    inventory_page.header.open_cart()
    assert cart_page.items() == [line(product)]
    expect(cart_page.header.cart_badge).to_have_text("1")
