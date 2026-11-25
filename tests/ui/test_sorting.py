"""Product sorting: all four options of the sort dropdown."""

from decimal import Decimal

import pytest

from framework.data.products import PRODUCTS, SortOption
from framework.pages.inventory_page import InventoryPage
from framework.testcase import tc

pytestmark = [pytest.mark.inventory, pytest.mark.regression]

# The page starts sorted A-Z, so each case first sorts the opposite way and checks
# the list moved. Otherwise the A-Z case would pass even if sorting did nothing.
OPPOSITE = {
    SortOption.NAME_ASC: SortOption.NAME_DESC,
    SortOption.NAME_DESC: SortOption.NAME_ASC,
    SortOption.PRICE_ASC: SortOption.PRICE_DESC,
    SortOption.PRICE_DESC: SortOption.PRICE_ASC,
}


def sort_key(page: InventoryPage, key: str) -> list[str] | list[Decimal]:
    """What the list is sorted by: the product names or the prices."""
    return page.product_names() if key == "name" else page.product_prices()


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
    inventory_page.sort_by(OPPOSITE[option])
    before = sort_key(inventory_page, key)
    assert before != sorted(before, reverse=reverse), "precondition: list never left the order"

    inventory_page.sort_by(option)
    names = inventory_page.product_names()
    prices = inventory_page.product_prices()
    assert sorted(names) == sorted(PRODUCTS), "products missing or extra"
    assert dict(zip(names, prices, strict=True)) == PRODUCTS, "a price doesn't match its name"
    actual = sort_key(inventory_page, key)
    assert actual == sorted(actual, reverse=reverse), f"not sorted by {option}"
    assert actual != sorted(actual, reverse=not reverse), "order didn't change"
