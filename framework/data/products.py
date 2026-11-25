"""The product catalog the tests expect, and the sort dropdown's options."""

from decimal import Decimal
from enum import StrEnum

# Name -> price, as shown to standard_user. Decimal, not float: 15.99 is exact.
PRODUCTS: dict[str, Decimal] = {
    "Sauce Labs Backpack": Decimal("29.99"),
    "Sauce Labs Bike Light": Decimal("9.99"),
    "Sauce Labs Bolt T-Shirt": Decimal("15.99"),
    "Sauce Labs Fleece Jacket": Decimal("49.99"),
    "Sauce Labs Onesie": Decimal("7.99"),
    "Test.allTheThings() T-Shirt (Red)": Decimal("15.99"),
}


class SortOption(StrEnum):
    """Option values of the ``product-sort-container`` dropdown."""

    NAME_ASC = "az"
    NAME_DESC = "za"
    PRICE_ASC = "lohi"
    PRICE_DESC = "hilo"
