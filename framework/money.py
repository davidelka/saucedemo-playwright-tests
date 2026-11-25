"""Turning prices shown on the page into exact numbers."""

import re
from decimal import Decimal

_PRICE = re.compile(r"\$(\d+(?:\.\d{2})?)")


def parse_price(text: str) -> Decimal:
    """``"$29.99"`` or ``"Item total: $29.99"`` -> ``Decimal("29.99")``."""
    match = _PRICE.search(text)
    if not match:
        raise ValueError(f"no price in {text!r}")
    return Decimal(match.group(1))
