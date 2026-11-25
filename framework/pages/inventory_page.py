"""The product list (``/inventory.html``)."""

import re
from decimal import Decimal

from playwright.sync_api import Locator, Page

from framework.components.header import Header
from framework.components.product_item import item_named
from framework.data.products import SortOption
from framework.money import parse_price


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

    def open(self) -> None:
        self.page.goto(self.PATH)

    def sort_by(self, option: SortOption) -> None:
        self.sort_select.select_option(option.value)

    def product_names(self) -> list[str]:
        self.items.first.wait_for()  # the list has rendered
        return self.items.get_by_test_id("inventory-item-name").all_inner_texts()

    def product_prices(self) -> list[Decimal]:
        self.items.first.wait_for()
        texts = self.items.get_by_test_id("inventory-item-price").all_inner_texts()
        return [parse_price(t) for t in texts]

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
