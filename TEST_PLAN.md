# Test Plan: Sauce Demo

Every automated test carries one test-case ID from this file, set with
`@tc("TC-<AREA>-<NNN>")` (for parametrized tests, one ID per case via
`pytest.param(..., marks=tc(...))`).

Nothing is checked before a run. Select what to run (`-m checkout`, `--tc TC-LOGIN-001`),
and after the run pytest writes **`reports/traceability.md`**. It lists every case below
with its result (passed, failed, expected failure, skipped, not run) and the tests that
ran it, plus any test without an ID and any ID missing from this file. In CI the same
report appears on the run's summary page.

Run by ID: `uv run pytest --tc TC-LOGIN-001` or `uv run pytest --tc TC-CART-001,TC-CART-002`.
The HTML report also has a **Test ID** column.

Known-bug cases (tag `bug`) live in their feature's test file and table.
Each runs as `standard_user` first as a control (it must pass), then as the buggy user,
where it's an expected failure linked to [BUGS.md](BUGS.md).

To run without this file, pass `--no-test-plan`: it is never read and no
traceability report is written. If the file is missing without the flag, the run
still completes and the terminal says the report was skipped.

**Status:** `Automated` = covered by a test in `tests/` · `Manual` = checked by hand,
see the notes · `Not automated` = deliberately left out, see STRATEGY.md.

**Priority:** P1 = blocks a purchase or login · P2 = core function degraded ·
P3 = minor or cosmetic.

## LOGIN: Login form

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-LOGIN-001 | Valid credentials open the Products page | P1 | login, smoke, happy | Automated |
| TC-LOGIN-002 | Wrong password shows "Username and password do not match…" | P1 | login, negative | Automated |
| TC-LOGIN-003 | Unknown username shows "Username and password do not match…" | P2 | login, negative | Automated |
| TC-LOGIN-004 | Locked-out user sees "Sorry, this user has been locked out." | P1 | login, negative | Automated |
| TC-LOGIN-005 | Empty username shows "Username is required" | P2 | login, negative | Automated |
| TC-LOGIN-006 | Empty password shows "Password is required" | P2 | login, negative | Automated |
| TC-LOGIN-007 | Opening /inventory.html without logging in shows the login form with an error | P1 | login, negative | Automated |

## AUTH: Saved session (storage state)

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-AUTH-001 | standard_user's saved session opens Products without the login form | P1 | login, smoke, happy | Automated |
| TC-AUTH-002 | problem_user's saved session opens Products | P2 | login, happy | Automated |
| TC-AUTH-003 | performance_glitch_user's saved session opens Products (slow login tolerated) | P2 | login, happy | Automated |
| TC-AUTH-004 | error_user's saved session opens Products | P2 | login, happy | Automated |
| TC-AUTH-005 | visual_user's saved session opens Products | P2 | login, happy | Automated |
| TC-AUTH-006 | A saved session older than the max age is re-created | P2 | login | Automated |

## INV: Product list

The only cases that know the expected catalog (`framework/data/products.py`). All other
cases read the products from the page, so a new or repriced product fails only TC-INV-001.

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-INV-001 | Product list matches the expected catalog (names and prices, no duplicates) | P2 | inventory, happy | Automated |
| TC-INV-002 | Each product has its own image (standard_user, control for TC-INV-003) | P2 | inventory, bug, user_standard | Automated |
| TC-INV-003 | Each product has its own image, problem_user (known bug BUG-002) | P2 | inventory, bug, user_problem | Automated |
| TC-INV-004 | Each product's link opens that product (standard_user, control for TC-INV-005) | P1 | inventory, bug, user_standard | Automated |
| TC-INV-005 | Each product's link opens that product, problem_user (known bug BUG-004) | P1 | inventory, bug, user_problem | Automated |

## SORT: Product sorting

The expected order is computed from the products the page shows. Each case first sorts
the opposite way and checks the list moved, so a sort that does nothing fails every case
(the page starts A-Z). Price sorts compare prices only: equal prices have no defined order.

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-SORT-001 | Name (A to Z): names in A-Z order, same products and prices as before sorting | P2 | inventory, happy, smoke | Automated |
| TC-SORT-002 | Name (Z to A): names in Z-A order, same products and prices as before sorting | P2 | inventory, happy | Automated |
| TC-SORT-003 | Price (low to high): ascending prices, same products and prices as before sorting | P2 | inventory, happy | Automated |
| TC-SORT-004 | Price (high to low): descending prices, same products and prices as before sorting | P2 | inventory, happy | Automated |
| TC-SORT-005 | Price sort works with no error alert (standard_user, control for TC-SORT-006/007) | P2 | inventory, bug, user_standard | Automated |
| TC-SORT-006 | Price sort works with no error alert, problem_user (known bug BUG-003) | P2 | inventory, bug, user_problem | Automated |
| TC-SORT-007 | Price sort works with no error alert, error_user (known bug BUG-008) | P2 | inventory, bug, user_error | Automated |

## CART: Cart

Cases use the first products the page shows and expect the price the product list showed.

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-CART-001 | Adding 2 products shows badge "2" and both in the cart at their listed price, quantity 1 | P1 | cart, happy, smoke | Automated |
| TC-CART-002 | Removing a product from the product list lowers the badge | P2 | cart, happy | Automated |
| TC-CART-003 | Removing the last item in the cart hides the badge and empties the cart | P2 | cart, negative | Automated |
| TC-CART-004 | Cart keeps its items after Continue Shopping and reopening it | P2 | cart, happy | Automated |
| TC-CART-005 | Every product can be added: badge and cart show them all (standard_user, control) | P1 | cart, bug, user_standard | Automated |
| TC-CART-006 | Every product can be added, problem_user (known bug BUG-005) | P1 | cart, bug, user_problem | Automated |
| TC-CART-007 | Every product can be added, error_user (known bug BUG-005) | P1 | cart, bug, user_error | Automated |
| TC-CART-008 | A product can be removed from the product list (standard_user, control) | P2 | cart, bug, user_standard | Automated |
| TC-CART-009 | A product can be removed from the product list, problem_user (known bug BUG-006) | P2 | cart, bug, user_problem | Automated |
| TC-CART-010 | A product can be removed from the product list, error_user (known bug BUG-006) | P2 | cart, bug, user_error | Automated |

## CHECKOUT: Checkout

Totals cases use the first products the page shows, and compute the expected item total,
8% tax (rounded to the cent, half up) and total from the prices the product list showed.

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-CHECKOUT-001 | One product: overview items, item total, tax, total correct; order completes, cart emptied | P1 | checkout, happy, smoke | Automated |
| TC-CHECKOUT-002 | Three products: overview items, item total, tax, total correct; order completes | P1 | checkout, happy | Automated |
| TC-CHECKOUT-003 | All products: overview items, item total, tax, total correct; order completes | P1 | checkout, happy | Automated |
| TC-CHECKOUT-004 | Missing first name shows "Error: First Name is required", stays on step one | P2 | checkout, negative | Automated |
| TC-CHECKOUT-005 | Missing last name shows "Error: Last Name is required", stays on step one | P2 | checkout, negative | Automated |
| TC-CHECKOUT-006 | Missing postal code shows "Error: Postal Code is required", stays on step one | P2 | checkout, negative | Automated |
| TC-CHECKOUT-007 | All fields empty shows the first-name error first, stays on step one | P3 | checkout, negative | Automated |
| TC-CHECKOUT-008 | An empty cart can't be checked out (known bug BUG-001, expected failure) | P2 | checkout, negative, bug | Automated |
| TC-CHECKOUT-009 | Checkout fields keep what you type (standard_user, control for TC-CHECKOUT-010/011) | P1 | checkout, bug, user_standard | Automated |
| TC-CHECKOUT-010 | Checkout fields keep what you type, problem_user (known bug BUG-007) | P1 | checkout, bug, user_problem | Automated |
| TC-CHECKOUT-011 | Checkout fields keep what you type, error_user (known bug BUG-009) | P2 | checkout, bug, user_error | Automated |
| TC-CHECKOUT-012 | Finish completes the order (standard_user, control for TC-CHECKOUT-013) | P1 | checkout, bug, user_standard | Automated |
| TC-CHECKOUT-013 | Finish completes the order, error_user (known bug BUG-010) | P1 | checkout, bug, user_error | Automated |

## CFG: Configuration

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-CFG-001 | Missing `SAUCE_PASSWORD` fails fast with a clear validation error | P2 | unit | Automated |
| TC-CFG-002 | Settings are read from `SAUCE_*` environment variables | P2 | unit | Automated |

## UNIT: Framework internals

| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-UNIT-001 | `tc()` rejects a malformed test-case ID | P3 | unit | Automated |
| TC-UNIT-002 | TEST_PLAN.md rows are parsed into ID, title and status | P2 | unit | Automated |
| TC-UNIT-003 | Report shows passed, failed and not-run plan cases | P2 | unit | Automated |
| TC-UNIT-004 | Report shows expected failures and skips | P2 | unit | Automated |
| TC-UNIT-005 | Report: worst outcome wins when one ID runs several times | P2 | unit | Automated |
| TC-UNIT-006 | Report lists tests without an ID and IDs not in the plan | P2 | unit | Automated |
| TC-UNIT-007 | `--tc` selects tests by ID; the rest show as not run | P3 | unit | Automated |
| TC-UNIT-008 | Report collects results from parallel (xdist) workers | P2 | unit | Automated |
| TC-UNIT-009 | Layer tag (`ui`, `unit`…) is added from the test's folder | P3 | unit | Automated |
| TC-UNIT-010 | User tag (`user_problem`…) is added from the user a test runs as | P3 | unit | Automated |
| TC-UNIT-011 | `--no-test-plan` runs the tests without reading the plan or writing the report | P3 | unit | Automated |
| TC-UNIT-012 | A missing TEST_PLAN.md skips the report with a message and never fails the run | P3 | unit | Automated |
| TC-UNIT-013 | `parse_price` reads prices from labels ("$7.99", "Item total: $29.99", "$0") | P2 | unit | Automated |
| TC-UNIT-014 | `expected_tax` is 8% rounded to the cent, half a cent rounding up | P2 | unit | Automated |
| TC-UNIT-015 | `parse_price` raises on text without a price instead of guessing | P3 | unit | Automated |
| TC-UNIT-016 | `xfail_bug`: a wrong result is an expected failure, linked to BUGS.md | P2 | unit | Automated |
| TC-UNIT-017 | `xfail_bug`: a broken test (other error) and a fixed bug (pass) both fail the run | P2 | unit | Automated |
| TC-UNIT-018 | `xfail_bug` rejects a malformed bug ID | P3 | unit | Automated |
