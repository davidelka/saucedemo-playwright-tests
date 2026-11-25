"""Known bugs on the product list (images, product links, sorting). See BUGS.md.

Each test runs as standard_user first: there it must pass, which proves the test
itself is right. For the buggy users it's an expected failure linked to BUGS.md.
"""

from operator import attrgetter

import pytest
from playwright.sync_api import expect

from framework.bugs import xfail_bug
from framework.data.users import User
from framework.pages.inventory_page import InventoryPage, SortOption
from framework.pages.product_page import ProductPage
from framework.testcase import tc

pytestmark = [pytest.mark.bug, pytest.mark.inventory, pytest.mark.regression]


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
    assert len(set(images)) == len(images), (
        f"{len(images)} products share {len(set(images))} image(s)"
    )


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
    assert opened == {name: name for name in opened}, "a link opened a different product"


@pytest.mark.parametrize(
    "user",
    [
        pytest.param(User.STANDARD, marks=tc("TC-SORT-005")),
        pytest.param(
            User.PROBLEM,
            marks=[tc("TC-SORT-006"), xfail_bug("BUG-003", "sorting has no effect")],
        ),
        pytest.param(
            User.ERROR,
            marks=[
                tc("TC-SORT-007"),
                xfail_bug("BUG-008", "sorting shows 'Sorting is broken!' and doesn't sort"),
            ],
        ),
    ],
)
def test_sorting_works_without_errors(
    inventory_page: InventoryPage, dialogs: list[str], user: User
) -> None:
    shown = inventory_page.products()
    expected = [f"${p.price}" for p in sorted(shown, key=attrgetter("price"))]
    inventory_page.sort_by(SortOption.PRICE_ASC)
    expect(inventory_page.price_labels).to_have_text(expected)
    assert dialogs == [], "the page showed an error alert"
