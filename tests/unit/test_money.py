"""Tests for price parsing and the expected tax (framework/money.py)."""

from decimal import Decimal

import pytest

from framework.money import expected_tax, parse_price
from framework.testcase import tc

pytestmark = pytest.mark.unit


@tc("TC-UNIT-013")
@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("$7.99", "7.99"),
        ("Item total: $29.99", "29.99"),
        ("Tax: $2.40", "2.40"),
        ("Total: $140.34", "140.34"),
        ("Item total: $0", "0"),  # how the site shows an empty cart's total
    ],
)
def test_parse_price(text: str, value: str) -> None:
    assert parse_price(text) == Decimal(value)


@tc("TC-UNIT-014")
@pytest.mark.parametrize(
    ("subtotal", "tax"),
    [
        ("29.99", "2.40"),
        ("53.97", "4.32"),
        ("129.94", "10.40"),
        ("0", "0.00"),
        pytest.param("0.0625", "0.01", id="half-cent-rounds-up"),  # 8% = 0.005 exactly
    ],
)
def test_expected_tax(subtotal: str, tax: str) -> None:
    assert expected_tax(Decimal(subtotal)) == Decimal(tax)


@tc("TC-UNIT-015")
def test_parse_price_rejects_text_without_price() -> None:
    with pytest.raises(ValueError, match="Total:"):
        parse_price("Total:")
