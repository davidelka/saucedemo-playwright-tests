"""Multi-page steps that several tests share."""

from framework.pages.cart_page import CartPage
from framework.pages.inventory_page import InventoryPage, Product


def start_checkout(
    inventory_page: InventoryPage, cart_page: CartPage, products: list[Product]
) -> None:
    """Add the products, open the cart and click Checkout."""
    for product in products:
        inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    cart_page.checkout()
