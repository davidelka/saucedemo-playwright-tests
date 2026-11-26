"""Response time: every page that shows the product list must appear within the budget.

The clock starts just before the click and stops when the product list is visible, so
it measures what a person waits for. Nothing sleeps: the test waits for the page and
reads the clock (see ``framework/timing.py``). The budget is ``page_budget_seconds`` in
the settings (2 s by default; ``SAUCE_PAGE_BUDGET_SECONDS`` changes it).

Each test runs as standard_user first, where it must pass (proving the test is right),
then as performance_glitch_user, where it's an expected failure (BUG-017). Only the
budget check inside ``bug_symptom()`` counts as the bug: a page that never appears
fails the run.
"""

import pytest

from framework.bugs import bug_symptom, xfail_bug
from framework.config import Settings
from framework.data.users import User
from framework.pages.cart_page import CartPage
from framework.pages.inventory_page import InventoryPage, SortOption
from framework.pages.login_page import LoginPage
from framework.pages.product_page import ProductPage
from framework.testcase import tc
from framework.timing import seconds_until

pytestmark = [pytest.mark.performance, pytest.mark.bug, pytest.mark.regression]


def standard_and_glitch_user(control_id: str, glitch_id: str) -> pytest.MarkDecorator:
    """Run as standard_user (the control) and as performance_glitch_user (BUG-017)."""
    return pytest.mark.parametrize(
        "user",
        [
            pytest.param(User.STANDARD, marks=tc(control_id)),
            pytest.param(
                User.PERFORMANCE_GLITCH,
                marks=[
                    tc(glitch_id),
                    xfail_bug("BUG-017", "the product list takes 5 seconds to appear"),
                ],
            ),
        ],
    )


def too_slow(seconds: float, budget: float) -> str:
    return f"the product list took {seconds:.2f} s; the budget is {budget} s"


@standard_and_glitch_user("TC-PERF-001", "TC-PERF-002")
def test_login_shows_products_within_budget(
    login_page: LoginPage, settings: Settings, user: User
) -> None:
    login_page.open()
    login_page.fill(user, settings.password.get_secret_value())
    seconds = seconds_until(login_page.submit, InventoryPage(login_page.page).product_list)
    budget = settings.page_budget_seconds
    with bug_symptom():
        assert seconds <= budget, too_slow(seconds, budget)


@standard_and_glitch_user("TC-PERF-003", "TC-PERF-004")
def test_sorting_finishes_within_budget(
    inventory_page: InventoryPage, settings: Settings, user: User
) -> None:
    # The list starts sorted A-Z, so Z-A always moves a different product to the top.
    names = [p.name for p in inventory_page.products()]
    last = max(names)
    assert names[0] != last, "precondition: sorting Z-A must change the first product"
    first_is_last = inventory_page.items.first.get_by_text(last, exact=True)
    seconds = seconds_until(lambda: inventory_page.sort_by(SortOption.NAME_DESC), first_is_last)
    budget = settings.page_budget_seconds
    with bug_symptom():
        assert seconds <= budget, too_slow(seconds, budget)


@standard_and_glitch_user("TC-PERF-005", "TC-PERF-006")
def test_back_to_products_within_budget(
    inventory_page: InventoryPage, product_page: ProductPage, settings: Settings, user: User
) -> None:
    inventory_page.open_product(inventory_page.products()[0].name)
    product_page.back_button.wait_for()  # on the product page (not timed)
    seconds = seconds_until(product_page.back, inventory_page.product_list)
    budget = settings.page_budget_seconds
    with bug_symptom():
        assert seconds <= budget, too_slow(seconds, budget)


@standard_and_glitch_user("TC-PERF-007", "TC-PERF-008")
def test_continue_shopping_within_budget(
    inventory_page: InventoryPage, cart_page: CartPage, settings: Settings, user: User
) -> None:
    inventory_page.header.open_cart()
    cart_page.continue_shopping_button.wait_for()  # on the cart page (not timed)
    seconds = seconds_until(cart_page.continue_shopping, inventory_page.product_list)
    budget = settings.page_budget_seconds
    with bug_symptom():
        assert seconds <= budget, too_slow(seconds, budget)
