"""Finding one product card (inventory list or cart row) by its exact name."""

import re

from playwright.sync_api import Locator


def item_named(items: Locator, name: str) -> Locator:
    """The card among ``items`` whose name element is exactly ``name``.

    Matches the name element only, not the whole card: a description can mention
    another product's text (the Backpack's says "carry.allTheThings()").
    """
    name_el = items.page.get_by_test_id("inventory-item-name")
    return items.filter(has=name_el.filter(has_text=re.compile(rf"^{re.escape(name)}$")))
