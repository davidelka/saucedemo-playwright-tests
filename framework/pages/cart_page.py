"""The cart (``/cart.html``)."""

import re
from dataclasses import dataclass
from decimal import Decimal

from playwright.sync_api import Locator, Page, expect

from framework.components.header import Header
from framework.components.product_item import item_named
from framework.money import parse_price


@dataclass(frozen=True)
class CartItem:
    """One cart row, as shown on the page."""

    name: str
    price: Decimal
    quantity: int


def read_cart_items(cart_list: Locator) -> list[CartItem]:
    """The rows of a cart list (the cart page and the checkout overview share it)."""
    # The URL changes before the page renders (single-page app), so wait for the
    # list itself, not the URL.
    expect(cart_list).to_be_visible()
    return [
        CartItem(
            name=row.get_by_test_id("inventory-item-name").inner_text(),
            price=parse_price(row.get_by_test_id("inventory-item-price").inner_text()),
            quantity=int(row.get_by_test_id("item-quantity").inner_text()),
        )
        for row in cart_list.get_by_test_id("inventory-item").all()
    ]


class CartPage:
    PATH = "/cart.html"
    URL = re.compile(re.escape(PATH) + "$")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.cart_list = page.get_by_test_id("cart-list")
        self.rows = self.cart_list.get_by_test_id("inventory-item")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    def items(self) -> list[CartItem]:
        return read_cart_items(self.cart_list)

    def remove(self, name: str) -> None:
        item_named(self.rows, name).get_by_role("button", name="Remove").click()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()

    def checkout(self) -> None:
        self.checkout_button.click()
