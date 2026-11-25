"""The product list (``/inventory.html``)."""

import re

from playwright.sync_api import Page


class InventoryPage:
    PATH = "/inventory.html"
    # For expect(page).to_have_url(): matches the full URL, whatever the base URL.
    URL = re.compile(re.escape(PATH) + "$")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.get_by_test_id("title")

    def open(self) -> None:
        self.page.goto(self.PATH)
