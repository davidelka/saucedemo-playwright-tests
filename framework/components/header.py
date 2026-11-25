"""The header shown on every page after login: cart link and badge."""

from playwright.sync_api import Page


class Header:
    def __init__(self, page: Page) -> None:
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        # The number of items in the cart; hidden when the cart is empty.
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")

    def open_cart(self) -> None:
        self.cart_link.click()
