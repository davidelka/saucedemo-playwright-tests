"""Product sorting: all four options of the sort dropdown.

The expected order is computed from the products the page shows, not from a fixed
catalog, so adding or repricing a product doesn't break these tests (the catalog
itself is checked once, in test_inventory.py).
"""

from operator import attrgetter

import pytest
from playwright.sync_api import expect

from framework.data.products import SortOption
from framework.pages.inventory_page import InventoryPage, Product
from framework.testcase import tc

pytestmark = [pytest.mark.inventory, pytest.mark.regression]

OPPOSITE = {
    SortOption.NAME_ASC: SortOption.NAME_DESC,
    SortOption.NAME_DESC: SortOption.NAME_ASC,
    SortOption.PRICE_ASC: SortOption.PRICE_DESC,
    SortOption.PRICE_DESC: SortOption.PRICE_ASC,
}


def label_texts(products: list[Product], key: str) -> list[str]:
    """The name or price labels the page shows for these products, in this order.

    Price sorts compare prices, not names: two products can cost the same, and the
    order between them isn't defined.
    """
    return [p.name for p in products] if key == "name" else [f"${p.price}" for p in products]


@pytest.mark.happy
@pytest.mark.parametrize(
    ("option", "key", "reverse"),
    [
        pytest.param(
            SortOption.NAME_ASC,
            "name",
            False,
            id="name-a-z",
            marks=[tc("TC-SORT-001"), pytest.mark.smoke],
        ),
        pytest.param(SortOption.NAME_DESC, "name", True, id="name-z-a", marks=tc("TC-SORT-002")),
        pytest.param(
            SortOption.PRICE_ASC, "price", False, id="price-low-high", marks=tc("TC-SORT-003")
        ),
        pytest.param(
            SortOption.PRICE_DESC, "price", True, id="price-high-low", marks=tc("TC-SORT-004")
        ),
    ],
)
def test_sort_orders_products(
    inventory_page: InventoryPage, option: SortOption, key: str, reverse: bool
) -> None:
    shown = inventory_page.products()
    expected = label_texts(sorted(shown, key=attrgetter(key), reverse=reverse), key)
    labels = inventory_page.name_labels if key == "name" else inventory_page.price_labels

    # The page starts sorted A-Z, so sort the opposite way first and check the list
    # moved. Otherwise the A-Z case would pass even if sorting did nothing.
    inventory_page.sort_by(OPPOSITE[option])
    expect(labels, "precondition: the list never left the target order").not_to_have_text(expected)

    inventory_page.sort_by(option)
    expect(labels).to_have_text(expected)  # retries until the page shows this order
    assert sorted(inventory_page.products()) == sorted(shown), "sorting changed the products"
