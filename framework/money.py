"""Turning prices shown on the page into exact numbers, and the tax the site should charge."""

import re
from decimal import ROUND_HALF_UP, Decimal

_PRICE = re.compile(r"\$(\d+(?:\.\d{2})?)")

TAX_RATE = Decimal("0.08")
CENT = Decimal("0.01")


def parse_price(text: str) -> Decimal:
    """``"$29.99"`` or ``"Item total: $29.99"`` -> ``Decimal("29.99")``."""
    match = _PRICE.search(text)
    if not match:
        raise ValueError(f"no price in {text!r}")
    return Decimal(match.group(1))


def expected_tax(subtotal: Decimal, rate: Decimal = TAX_RATE) -> Decimal:
    """Tax on ``subtotal``, rounded to the cent, half a cent rounding up."""
    return (subtotal * rate).quantize(CENT, rounding=ROUND_HALF_UP)
