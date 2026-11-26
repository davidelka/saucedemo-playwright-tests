"""Turning prices shown on the page into exact numbers, and the tax the site should charge."""

import re
from decimal import ROUND_HALF_UP, Decimal

# A price label as the site shows it: "$29.99" or "Item total: $29.99". The whole text
# must match, so "-$5.00" or "$1,299.00" raise instead of being misread.
_PRICE = re.compile(r"(?:[^$]*:\s*)?\$(\d+(?:\.\d+)?)")

TAX_RATE = Decimal("0.08")
CENT = Decimal("0.01")


def parse_price(text: str) -> Decimal:
    """``"$29.99"`` or ``"Item total: $29.99"`` -> ``Decimal("29.99")``.

    Reads the number exactly as shown (``"$89.8"`` -> 89.8), never rounding or cutting
    digits, so a wrongly shown price fails the comparison instead of hiding.
    """
    match = _PRICE.fullmatch(text.strip())
    if not match:
        raise ValueError(f"no price in {text!r}")
    return Decimal(match.group(1))


def expected_tax(subtotal: Decimal, rate: Decimal = TAX_RATE) -> Decimal:
    """Tax on ``subtotal``, rounded to the cent, half a cent rounding up."""
    return (subtotal * rate).quantize(CENT, rounding=ROUND_HALF_UP)
