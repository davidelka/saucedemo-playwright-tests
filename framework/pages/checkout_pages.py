"""The three checkout steps: your information, overview, complete."""

import re
from decimal import Decimal

from playwright.sync_api import Page

from framework.components.header import Header
from framework.data.customer import Customer
from framework.money import parse_price
from framework.pages.cart_page import CartItem, read_cart_items


class CheckoutInfoPage:
    """Step one: first name, last name, postal code."""

    PATH = "/checkout-step-one.html"
    URL = re.compile(re.escape(PATH) + "$")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.error = page.get_by_test_id("error")

    def fill(self, customer: Customer) -> None:
        self.first_name.fill(customer.first_name)
        self.last_name.fill(customer.last_name)
        self.postal_code.fill(customer.postal_code)

    def continue_(self) -> None:  # trailing underscore: "continue" is a Python keyword
        self.continue_button.click()


class CheckoutOverviewPage:
    """Step two: the items, item total, tax and total."""

    PATH = "/checkout-step-two.html"
    URL = re.compile(re.escape(PATH) + "$")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cart_list = page.get_by_test_id("cart-list")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.finish_button = page.get_by_test_id("finish")

    def items(self) -> list[CartItem]:
        return read_cart_items(self.cart_list)

    def subtotal(self) -> Decimal:
        return parse_price(self.subtotal_label.inner_text())

    def tax(self) -> Decimal:
        return parse_price(self.tax_label.inner_text())

    def total(self) -> Decimal:
        return parse_price(self.total_label.inner_text())

    def finish(self) -> None:
        self.finish_button.click()


class CheckoutCompletePage:
    """The confirmation page."""

    PATH = "/checkout-complete.html"
    URL = re.compile(re.escape(PATH) + "$")

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = Header(page)
        self.complete_header = page.get_by_test_id("complete-header")
        self.back_home_button = page.get_by_test_id("back-to-products")
