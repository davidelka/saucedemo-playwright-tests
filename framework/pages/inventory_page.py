"""The product list (``/inventory.html``)."""

import re
from dataclasses import dataclass
from decimal import Decimal

from playwright.sync_api import Locator, Page

from framework.components.header import Header
from framework.components.product_item import item_named
from framework.data.products import SortOption
from framework.money import parse_price


@dataclass(frozen=True, order=True)
class Product:
    """One product card, as shown on the page."""

    name: str
    price: Decimal


class InventoryPage:
    PATH = "/inventory.html"
    # For expect(page).to_have_url(): matches the full URL, whatever the base URL.
    URL = re.compile(re.escape(PATH) + "$")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.title = page.get_by_test_id("title")
        self.sort_select = page.get_by_test_id("product-sort-container")
        self.items = page.get_by_test_id("inventory-item")
        # One label per card, in display order. Use with expect(...).to_have_text([...]).
        self.name_labels = self.items.get_by_test_id("inventory-item-name")
        self.price_labels = self.items.get_by_test_id("inventory-item-price")

    def open(self) -> None:
        self.page.goto(self.PATH)

    def sort_by(self, option: SortOption) -> None:
        self.sort_select.select_option(option.value)

    def products(self) -> list[Product]:
        """Every product shown, in display order (a snapshot: it reads once, no retry)."""
        # all_inner_texts() doesn't wait, so first wait for the list to render.
        self.items.first.wait_for()
        names = self.name_labels.all_inner_texts()
        prices = self.price_labels.all_inner_texts()
        return [Product(n, parse_price(p)) for n, p in zip(names, prices, strict=True)]

    def product_images(self) -> list[str]:
        """The ``src`` of each product image, in display order."""
        self.items.first.wait_for()
        return [img.get_attribute("src") or "" for img in self.items.locator("img").all()]

    def item(self, name: str) -> Locator:
        return item_named(self.items, name)

    def add_to_cart(self, name: str) -> None:
        self.item(name).get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, name: str) -> None:
        self.item(name).get_by_role("button", name="Remove").click()
