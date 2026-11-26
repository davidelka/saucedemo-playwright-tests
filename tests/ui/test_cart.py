"""Cart: badge count, cart contents (names, prices, quantities), removing items.

Tests pick the first products the page shows rather than naming them, and expect the
price the product list showed. So they test that the cart shows what you added, at
the price you saw, and keep working if the catalog changes.

Tests tagged ``bug`` also cover known bugs (see BUGS.md): they run as standard_user
first, where they must pass (proving the test is right), then as each buggy user,
where they're an expected failure. Only the check inside ``bug_symptom()`` counts
as the bug; a failure before it fails the run.
"""

import pytest
from playwright.sync_api import expect

from framework.bugs import bug_symptom, xfail_bug
from framework.data.users import User
from framework.pages.cart_page import CartItem, CartPage
from framework.pages.inventory_page import InventoryPage, Product
from framework.testcase import tc

pytestmark = [pytest.mark.cart, pytest.mark.regression]

ADD_BUG = ("BUG-005", "Add to cart does nothing for some products")
REMOVE_BUG = ("BUG-006", "Remove on the product list does nothing")


def line(product: Product) -> CartItem:
    """The cart line expected for one unit of a product, at its listed price."""
    return CartItem(product.name, product.price, 1)


@tc("TC-CART-001")
@pytest.mark.smoke
@pytest.mark.happy
def test_add_products_updates_badge_and_cart(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    first, second = inventory_page.products()[:2]
    inventory_page.add_to_cart(first.name)
    inventory_page.add_to_cart(second.name)
    expect(inventory_page.header.cart_badge).to_have_text("2")

    inventory_page.header.open_cart()
    assert cart_page.items() == [line(first), line(second)]


@tc("TC-CART-002")
@pytest.mark.happy
def test_remove_from_inventory_leaves_the_other_product(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    first, second = inventory_page.products()[:2]
    inventory_page.add_to_cart(first.name)
    inventory_page.add_to_cart(second.name)
    inventory_page.remove_from_cart(first.name)
    expect(inventory_page.header.cart_badge).to_have_text("1")
    inventory_page.header.open_cart()
    assert cart_page.items() == [line(second)], "the wrong product was removed"


@tc("TC-CART-003")
@pytest.mark.negative
def test_remove_last_item_empties_cart(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    product = inventory_page.products()[0]
    inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    cart_page.remove(product.name)
    expect(cart_page.header.cart_badge).to_be_hidden()
    assert cart_page.items() == []


@tc("TC-CART-004")
@pytest.mark.happy
def test_cart_persists_across_navigation(
    inventory_page: InventoryPage, cart_page: CartPage
) -> None:
    product = inventory_page.products()[0]
    inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    cart_page.continue_shopping()
    expect(inventory_page.title).to_have_text("Products")
    inventory_page.header.open_cart()
    assert cart_page.items() == [line(product)]
    expect(cart_page.header.cart_badge).to_have_text("1")


@pytest.mark.bug
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CART-005")),
        pytest.param(User.PROBLEM, marks=[tc("TC-CART-006"), xfail_bug(*ADD_BUG)]),
        pytest.param(User.ERROR, marks=[tc("TC-CART-007"), xfail_bug(*ADD_BUG)]),
    ],
)
def test_every_product_can_be_added(
    inventory_page: InventoryPage, cart_page: CartPage, user: User
) -> None:
    products = inventory_page.products()
    for product in products:
        inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    in_cart = cart_page.items()
    with bug_symptom():
        expect(cart_page.header.cart_badge).to_have_text(str(len(products)))
        assert in_cart == [line(p) for p in products]


@pytest.mark.bug
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CART-008")),
        pytest.param(User.PROBLEM, marks=[tc("TC-CART-009"), xfail_bug(*REMOVE_BUG)]),
        pytest.param(User.ERROR, marks=[tc("TC-CART-010"), xfail_bug(*REMOVE_BUG)]),
    ],
)
def test_product_can_be_removed_from_the_list(inventory_page: InventoryPage, user: User) -> None:
    product = inventory_page.products()[0]
    inventory_page.add_to_cart(product.name)
    expect(inventory_page.header.cart_badge).to_have_text("1")
    inventory_page.remove_from_cart(product.name)
    with bug_symptom():
        expect(inventory_page.header.cart_badge).to_be_hidden()


@pytest.mark.bug
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-CART-011")),
        pytest.param(
            User.VISUAL,
            marks=[
                tc("TC-CART-012"),
                xfail_bug("BUG-011", "the product list shows prices the cart doesn't charge"),
            ],
        ),
    ],
)
def test_cart_charges_the_listed_price(
    inventory_page: InventoryPage, cart_page: CartPage, user: User
) -> None:
    listed = inventory_page.products()
    for product in listed:
        inventory_page.add_to_cart(product.name)
    inventory_page.header.open_cart()
    in_cart = cart_page.items()
    names = [item.name for item in in_cart]
    assert names == [p.name for p in listed], "precondition: every product is in the cart"
    with bug_symptom():
        assert [item.price for item in in_cart] == [p.price for p in listed], (
            "the cart charges a different price than the product list showed"
        )
