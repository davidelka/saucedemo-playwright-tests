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
@pytest.mark.parametrize(
    "text",
    [
        pytest.param("Total:", id="no-price"),
        pytest.param("Total: -$32.39", id="minus-sign"),
        pytest.param("$1,299.00", id="thousands-separator"),
        pytest.param("Total: $32.39 USD", id="text-after-price"),
    ],
)
def test_parse_price_rejects_text_that_is_not_a_price(text: str) -> None:
    with pytest.raises(ValueError, match="no price in"):
        parse_price(text)


@tc("TC-UNIT-022")
@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("$89.8", "89.8"),
        ("$32.399", "32.399"),
        ("Item total: $105.96000000000001", "105.96000000000001"),
    ],
)
def test_parse_price_keeps_every_digit_shown(text: str, value: str) -> None:
    # Never round or cut: a wrongly shown price must fail the comparison, not hide.
    assert parse_price(text) == Decimal(value)
