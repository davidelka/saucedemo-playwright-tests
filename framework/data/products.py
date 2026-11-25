"""The product catalog the tests expect."""

from decimal import Decimal

# Name -> price, as shown to standard_user. Decimal, not float: 15.99 is exact.
# Only TC-INV-001 uses this; other tests read products from the page, so a catalog
# change means editing this dict, not the tests.
PRODUCTS: dict[str, Decimal] = {
    "Sauce Labs Backpack": Decimal("29.99"),
    "Sauce Labs Bike Light": Decimal("9.99"),
    "Sauce Labs Bolt T-Shirt": Decimal("15.99"),
    "Sauce Labs Fleece Jacket": Decimal("49.99"),
    "Sauce Labs Onesie": Decimal("7.99"),
    "Test.allTheThings() T-Shirt (Red)": Decimal("15.99"),
}
