"""A product's details page (``/inventory-item.html?id=N``)."""

from playwright.sync_api import Page

from framework.components.header import Header


class ProductPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.name = page.get_by_test_id("inventory-item-name")
        self.price = page.get_by_test_id("inventory-item-price")
        self.back_button = page.get_by_test_id("back-to-products")

    def back(self) -> None:
        self.back_button.click()
