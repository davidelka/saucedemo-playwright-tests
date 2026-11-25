"""Cart: badge count, cart contents (names, prices, quantities), removing items."""

import pytest
from playwright.sync_api import expect

from framework.data.products import PRODUCTS
from framework.pages.cart_page import CartItem, CartPage
from framework.pages.inventory_page import InventoryPage
from framework.testcase import tc

pytestmark = [pytest.mark.cart, pytest.mark.regression]

BACKPACK = "Sauce Labs Backpack"
ONESIE = "Sauce Labs Onesie"


def line(name: str) -> CartItem:
    """The cart line expected for one unit of a product."""
    return CartItem(name, PRODUCTS[name], 1)


@tc("TC-CART-001")
@pytest.mark.smoke
@pytest.mark.happy
def test_add_products_updates_badge_and_cart(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.add_to_cart(ONESIE)
    expect(inventory_page.header.cart_badge).to_have_text("2")

    inventory_page.header.open_cart()
    assert cart_page.items() == [line(BACKPACK), line(ONESIE)]


@tc("TC-CART-002")
@pytest.mark.happy
def test_remove_from_inventory_updates_badge(inventory_page: InventoryPage) -> None:
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.add_to_cart(ONESIE)
    inventory_page.remove_from_cart(BACKPACK)
    expect(inventory_page.header.cart_badge).to_have_text("1")


@tc("TC-CART-003")
@pytest.mark.negative
def test_remove_last_item_empties_cart(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.header.open_cart()
    cart_page.remove(BACKPACK)
    expect(cart_page.header.cart_badge).to_be_hidden()
    assert cart_page.items() == []


@tc("TC-CART-004")
@pytest.mark.happy
def test_cart_persists_across_navigation(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.header.open_cart()
    cart_page.continue_shopping()
    expect(inventory_page.title).to_have_text("Products")
    inventory_page.header.open_cart()
    assert cart_page.items() == [line(BACKPACK)]
    expect(cart_page.header.cart_badge).to_have_text("1")
