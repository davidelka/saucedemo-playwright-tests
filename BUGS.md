# Bugs

Found on https://www.saucedemo.com on 2026-11-26 (Playwright 1.65.2, Chromium and Firefox).
`problem_user` and `error_user` were compared action by action against `standard_user`;
only differences that reproduce are listed.

Every bug has an automated test marked with `xfail_bug(...)` (see `framework/bugs.py`):

- Today the test **fails as expected**, reported as `xfailed` (🟡 "expected failure (known bug)"
  in `reports/traceability.md`), so the run stays green.
- Only the bug's own check counts: the check inside `with bug_symptom():`. If the test
  fails before it (a page that didn't load, a setup step, a timeout), the run fails.
- The day the bug is fixed, the test passes and the run **fails** with `XPASS(strict)`.
  That's the signal to remove the marker and close the bug.
- Tests that run as several users also run as `standard_user`, where they must pass: that
  proves the test checks the right thing.
- Bug tests live with the other tests of their feature (`tests/ui/test_cart.py` and so on),
  tagged `bug`. When a bug is fixed, only its `xfail_bug` marker is removed.

Run only the bug tests:

```bash
uv run pytest -m bug -rx
```

**Severity:** Critical = login or purchase impossible for everyone · High = a core flow is
broken (a user can't buy, or may buy the wrong thing) or money values are wrong · Medium =
wrong behavior with a workaround, or bad data · Low = cosmetic.

## Summary

| Bug | Title | User | Severity | Test |
|-----|-------|------|----------|------|
| [BUG-001](#bug-001) | Checkout is allowed with an empty cart | standard_user | Medium | TC-CHECKOUT-008 |
| [BUG-002](#bug-002) | All products show the same image | problem_user | Medium | TC-INV-003 |
| [BUG-003](#bug-003) | Sorting has no effect | problem_user | Medium | TC-SORT-006 |
| [BUG-004](#bug-004) | Product links open the wrong product | problem_user | High | TC-INV-005 |
| [BUG-005](#bug-005) | Add to cart does nothing for 3 of 6 products | problem_user, error_user | High | TC-CART-006, TC-CART-007 |
| [BUG-006](#bug-006) | Remove on the product list does nothing | problem_user, error_user | Medium | TC-CART-009, TC-CART-010 |
| [BUG-007](#bug-007) | Typing the last name overwrites the first name | problem_user | High | TC-CHECKOUT-010 |
| [BUG-008](#bug-008) | Sorting shows "Sorting is broken!" and doesn't sort | error_user | Medium | TC-SORT-007, TC-SORT-009 |
| [BUG-009](#bug-009) | Last Name ignores typing, checkout continues without it | error_user | Medium | TC-CHECKOUT-011, TC-CHECKOUT-015 |
| [BUG-010](#bug-010) | Finish doesn't complete the order | error_user | High | TC-CHECKOUT-013 |
| [BUG-011](#bug-011) | The product list shows prices the cart doesn't charge | visual_user | High | TC-CART-012 |
| [BUG-012](#bug-012) | Sauce Labs Backpack shows the "image not found" picture | visual_user | Low | TC-INV-007 |
| [BUG-013](#bug-013) | With four products, the item total shows float rounding digits | standard_user | Low | TC-CHECKOUT-017 |
| [BUG-014](#bug-014) | Checkout accepts names and postal code made only of spaces | standard_user | Medium | TC-CHECKOUT-018 |
| [BUG-015](#bug-015) | The About link goes to an error page | problem_user | Low | TC-MENU-004 |
| [BUG-016](#bug-016) | Reset App State leaves the products' buttons on "Remove" | standard_user | Medium | TC-MENU-005 |

## BUG-001

**Checkout is allowed with an empty cart, and places an empty order**

| | |
|---|---|
| Severity | Medium: creates orders with no items (bad data), no money is lost |
| User | `standard_user` (other users not checked) |
| Test | TC-CHECKOUT-008, `tests/ui/test_checkout.py::test_empty_cart_cannot_be_checked_out` |
| Found | Manually (David), then confirmed with a script |

**Steps**

1. Log in as `standard_user` with an empty cart (no badge on the cart icon).
2. Open the cart. It has no items. Click **Checkout**.
3. Fill in First Name, Last Name and Postal Code, then click **Continue**.
4. Click **Finish**.

**Expected:** An empty cart can't be checked out: the Checkout button is disabled, or
clicking it keeps you on the cart page with a message.

**Actual:** Step 2 opens "Checkout: Your Information". Step 3 shows an overview with
`Item total: $0`, `Tax: $0.00`, `Total: $0.00` (the item total is also formatted
differently from other prices). Step 4 shows "Thank you for your order!".

## BUG-002

**All products show the same image**

| | |
|---|---|
| Severity | Medium: customers can't see what they're buying; nothing is blocked |
| User | `problem_user` |
| Test | TC-INV-003, `tests/ui/test_inventory.py::test_each_product_has_its_own_image` |

**Steps**

1. Log in as `problem_user`.
2. Look at the product list.

**Expected:** Each product shows its own photo, as for `standard_user`.

**Actual:** All six products show the same placeholder image (`sl-404-….jpg`).

## BUG-003

**Sorting has no effect**

| | |
|---|---|
| Severity | Medium: a listed feature doesn't work; you can still browse all products |
| User | `problem_user` |
| Test | TC-SORT-006, `tests/ui/test_sorting.py::test_sorting_changes_the_order` |

**Steps**

1. Log in as `problem_user`.
2. Choose "Name (Z to A)", "Price (low to high)" or "Price (high to low)" in the sort menu.

**Expected:** The list is re-ordered, as for `standard_user`.

**Actual:** The list stays in the default A-Z order. No message is shown.

## BUG-004

**Product links open the wrong product**

| | |
|---|---|
| Severity | High: a customer may add the wrong item; one product's page can't be opened at all |
| User | `problem_user` |
| Test | TC-INV-005, `tests/ui/test_inventory.py::test_product_link_opens_that_product` |

**Steps**

1. Log in as `problem_user`.
2. Click a product's name in the product list.

**Expected:** That product's details page opens.

**Actual:** A different product opens: Backpack → Fleece Jacket, Bike Light → Bolt T-Shirt,
Bolt T-Shirt → Onesie, Onesie → Test.allTheThings() T-Shirt (Red), Test.allTheThings()
T-Shirt (Red) → Backpack. Fleece Jacket opens a page saying "ITEM NOT FOUND".

## BUG-005

**Add to cart does nothing for 3 of 6 products**

| | |
|---|---|
| Severity | High: half the catalog can't be bought |
| User | `problem_user`, `error_user` |
| Test | TC-CART-006, TC-CART-007, `tests/ui/test_cart.py::test_every_product_can_be_added` |

**Steps**

1. Log in as `problem_user` or `error_user`.
2. Click **Add to cart** on Sauce Labs Bolt T-Shirt, Sauce Labs Fleece Jacket or
   Test.allTheThings() T-Shirt (Red).

**Expected:** The button changes to **Remove**, the cart badge counts up, and the product
is in the cart.

**Actual:** The button stays **Add to cart**, the badge doesn't change, and the product
isn't in the cart. Backpack, Bike Light and Onesie can be added.

## BUG-006

**Remove on the product list does nothing**

| | |
|---|---|
| Severity | Medium: workaround exists (Remove on the cart page works) |
| User | `problem_user`, `error_user` |
| Test | TC-CART-009, TC-CART-010, `tests/ui/test_cart.py::test_product_can_be_removed_from_the_list` |

**Steps**

1. Log in as `problem_user` or `error_user`.
2. Click **Add to cart** on Sauce Labs Backpack. The badge shows 1.
3. Click **Remove** on the same product in the product list.

**Expected:** The button changes back to **Add to cart** and the badge disappears.

**Actual:** The button stays **Remove** and the badge stays at 1 (seen for every product
that can be added: Backpack, Bike Light, Onesie). Removing it on the cart page works.

## BUG-007

**Typing the last name overwrites the first name, so checkout can't continue**

| | |
|---|---|
| Severity | High: this user can't complete any purchase |
| User | `problem_user` |
| Test | TC-CHECKOUT-010, `tests/ui/test_checkout.py::test_checkout_fields_keep_what_you_type` |

**Steps**

1. Log in as `problem_user`, add Sauce Labs Backpack, open the cart, click **Checkout**.
2. Enter First Name `John`, Last Name `Doe`, Postal Code `12345`.
3. Click **Continue**.

**Expected:** The fields show John / Doe / 12345 and the overview opens.

**Actual:** After step 2, First Name shows `Doe` and Last Name is empty. Step 3 shows
"Error: Last Name is required", whatever you enter.

## BUG-008

**Sorting shows "Sorting is broken!" and doesn't sort**

| | |
|---|---|
| Severity | Medium: a listed feature doesn't work and shows an error; browsing still works |
| User | `error_user` |
| Test | TC-SORT-007, `tests/ui/test_sorting.py::test_sorting_changes_the_order` (no sorting); TC-SORT-009, `test_sorting_shows_no_error_alert` (the alert) |

**Steps**

1. Log in as `error_user`.
2. Choose any option in the sort menu.

**Expected:** The list is re-ordered, with no error.

**Actual:** An alert says "Sorting is broken! This error has been reported to Backtrace."
and the list stays in the default order. The browser console logs
"Error: This component failed to render!".

## BUG-009

**Last Name ignores typing, and checkout continues without a last name**

| | |
|---|---|
| Severity | Medium: orders are placed without a last name (bad data); required-field check bypassed |
| User | `error_user` |
| Test | TC-CHECKOUT-011, `tests/ui/test_checkout.py::test_checkout_fields_keep_what_you_type` (the field ignores typing); TC-CHECKOUT-015, `test_empty_last_name_blocks_checkout` (Continue goes ahead with Last Name empty) |

**Steps**

1. Log in as `error_user`, add Sauce Labs Backpack, open the cart, click **Checkout**.
2. Enter First Name `John`, Last Name `Doe`, Postal Code `12345`.
3. Click **Continue**.

**Expected:** Last Name shows `Doe`. (With an empty Last Name, `standard_user` gets
"Error: Last Name is required".)

**Actual:** Last Name stays empty, yet **Continue** opens the overview, so the order goes
ahead without a last name.

## BUG-010

**Finish doesn't complete the order**

| | |
|---|---|
| Severity | High: this user can't complete any purchase |
| User | `error_user` |
| Test | TC-CHECKOUT-013, `tests/ui/test_checkout.py::test_finish_completes_the_order` |

**Steps**

1. Log in as `error_user`, add Sauce Labs Backpack, open the cart, click **Checkout**.
2. Fill in the form, click **Continue**, then click **Finish**.

**Expected:** "Thank you for your order!" is shown.

**Actual:** Nothing happens: the page stays on "Checkout: Overview".

## BUG-011

**The product list shows prices the cart doesn't charge**

| | |
|---|---|
| Severity | High: the price a customer sees isn't the price they pay |
| User | `visual_user` |
| Test | TC-CART-012, `tests/ui/test_cart.py::test_cart_charges_the_listed_price` |

**Steps**

1. Log in as `visual_user` and note the prices on the product list.
2. Reload the page and note them again.
3. Add Sauce Labs Backpack to the cart and open the cart.

**Expected:** The list shows the same prices on every load, and the cart charges the price
the list showed.

**Actual:** The list shows different random prices on every load (for example `$52.35`, then
`$4.12`; some with one decimal, such as `$6.5`). The cart and checkout charge the real
price, `$29.99` for the backpack.

## BUG-012

**Sauce Labs Backpack shows the "image not found" picture**

| | |
|---|---|
| Severity | Low: cosmetic |
| User | `visual_user` |
| Test | TC-INV-007, `tests/ui/test_inventory.py::test_no_product_shows_the_not_found_image` |

**Steps**

1. Log in as `visual_user`.
2. Look at Sauce Labs Backpack on the product list.

**Expected:** The backpack's photo, as `standard_user` sees it.

**Actual:** The site's "image not found" picture (`sl-404…jpg`), the same one `problem_user`
sees for every product ([BUG-002](#bug-002)).

## BUG-013

**With four products, the item total shows float rounding digits**

| | |
|---|---|
| Severity | Low: cosmetic; the amount, tax and total are right, only the item total's display is wrong |
| User | `standard_user` (all users) |
| Test | TC-CHECKOUT-017, `tests/ui/test_checkout.py::test_item_total_shows_dollars_and_cents` |

**Steps**

1. Log in as `standard_user`.
2. Add Sauce Labs Backpack, Bike Light, Bolt T-Shirt and Fleece Jacket (the first four in
   the list).
3. Open the cart, click **Checkout**, fill in the form and click **Continue**.

**Expected:** "Item total: $105.96".

**Actual:** "Item total: $105.96000000000001". Tax ($8.48) and Total ($114.44) are right.
The site seems to add the prices as floating-point numbers and print the sum without
rounding: 1, 2, 3, 5 or 6 products (in list order) happen to add up exactly, so only some
carts show it.

## BUG-014

**Checkout accepts names and postal code made only of spaces**

| | |
|---|---|
| Severity | Medium: orders go through without real customer details (bad data) |
| User | `standard_user` (all users) |
| Test | TC-CHECKOUT-018, `tests/ui/test_checkout.py::test_fields_with_only_spaces_are_rejected` |

**Steps**

1. Log in as `standard_user`, add a product, open the cart and click **Checkout**.
2. Type three spaces into First Name, Last Name and Postal Code.
3. Click **Continue**.

**Expected:** "Error: First Name is required", as with empty fields.

**Actual:** The overview opens, and the order can be finished.

## BUG-015

**The About link goes to an error page**

| | |
|---|---|
| Severity | Low: a secondary link, not part of shopping |
| User | `problem_user` |
| Test | TC-MENU-004, `tests/ui/test_menu.py::test_about_link_points_to_sauce_labs` |

**Steps**

1. Log in as `problem_user`.
2. Open the menu (☰) and click **About** (or look at where it points).

**Expected:** https://saucelabs.com/, as for `standard_user`.

**Actual:** https://saucelabs.com/error/404, a "page not found" page.

## BUG-016

**Reset App State leaves the products' buttons on "Remove"**

| | |
|---|---|
| Severity | Medium: wrong behavior with a workaround (reloading the page fixes the buttons) |
| User | `standard_user` (all users) |
| Test | TC-MENU-005, `tests/ui/test_menu.py::test_reset_app_state_empties_the_cart` |

**Steps**

1. Log in as `standard_user` and add two products to the cart.
2. Open the menu (☰) and click **Reset App State**.

**Expected:** The cart badge disappears, and every product's button reads **Add to cart**.

**Actual:** The badge disappears, but the two products still show **Remove** until the page
is reloaded. The test has no control case, because `standard_user` has this bug.
