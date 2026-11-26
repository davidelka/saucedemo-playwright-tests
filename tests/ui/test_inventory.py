"""The product list itself: the one place that knows the expected catalog.

Every other test reads products from the page, so a catalog change (new product,
new price) fails only this test, and the fix is editing framework/data/products.py.

Tests tagged ``bug`` also cover known bugs (see BUGS.md): they run as standard_user
first, where they must pass (proving the test is right), then as each buggy user,
where they're an expected failure. Only the check inside ``bug_symptom()`` counts
as the bug; a failure before it fails the run.
"""

import pytest
from playwright.sync_api import expect

from framework.bugs import bug_symptom, xfail_bug
from framework.data.products import PRODUCTS
from framework.data.users import User
from framework.pages.inventory_page import InventoryPage
from framework.pages.product_page import ProductPage
from framework.testcase import tc

pytestmark = [pytest.mark.inventory, pytest.mark.regression]


@tc("TC-INV-001")
@pytest.mark.happy
def test_catalog_matches_expected(inventory_page: InventoryPage) -> None:
    products = inventory_page.products()
    shown = {p.name: p.price for p in products}
    assert len(shown) == len(products), "the same product name appears twice"
    assert shown == PRODUCTS


@pytest.mark.bug
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-INV-002")),
        pytest.param(
            User.PROBLEM,
            marks=[tc("TC-INV-003"), xfail_bug("BUG-002", "all products show the same image")],
        ),
    ],
)
def test_each_product_has_its_own_image(inventory_page: InventoryPage, user: User) -> None:
    images = inventory_page.product_images()
    with bug_symptom():
        assert len(set(images)) == len(images), (
            f"{len(images)} products share {len(set(images))} image(s)"
        )


@pytest.mark.bug
@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-INV-004")),
        pytest.param(
            User.PROBLEM,
            marks=[tc("TC-INV-005"), xfail_bug("BUG-004", "product links open the wrong product")],
        ),
    ],
)
def test_product_link_opens_that_product(
    inventory_page: InventoryPage, product_page: ProductPage, user: User
) -> None:
    opened = {}
    for product in inventory_page.products():
        inventory_page.open_product(product.name)
        expect(product_page.back_button).to_be_visible()  # the details page has rendered
        opened[product.name] = product_page.name.inner_text()
        product_page.back()
    # Collect every product first, so one failure shows all the wrong links.
    with bug_symptom():
        assert opened == {name: name for name in opened}, "a link opened a different product"
