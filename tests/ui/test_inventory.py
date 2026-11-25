"""The product list itself: the one place that knows the expected catalog.

Every other test reads products from the page, so a catalog change (new product,
new price) fails only this test, and the fix is editing framework/data/products.py.
"""

import pytest

from framework.data.products import PRODUCTS
from framework.pages.inventory_page import InventoryPage
from framework.testcase import tc

pytestmark = [pytest.mark.inventory, pytest.mark.regression]


@tc("TC-INV-001")
@pytest.mark.happy
def test_catalog_matches_expected(inventory_page: InventoryPage) -> None:
    products = inventory_page.products()
    shown = {p.name: p.price for p in products}
    assert len(shown) == len(products), "the same product name appears twice"
    assert shown == PRODUCTS
