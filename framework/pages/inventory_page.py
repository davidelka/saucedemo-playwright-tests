"""The product list (``/inventory.html``)."""

from playwright.sync_api import Page


class InventoryPage:
    PATH = "/inventory.html"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.get_by_test_id("title")

    def open(self) -> None:
        self.page.goto(self.PATH)
