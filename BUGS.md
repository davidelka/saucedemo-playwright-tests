# Bugs

Every bug here has an automated test marked with `xfail_bug(...)` (see `framework/bugs.py`):

- Today the test **fails as expected**, reported as `xfailed` (🟡 "expected failure (known bug)"
  in `reports/traceability.md`), so the run stays green.
- Only a wrong result counts (`AssertionError`). If the test breaks for another reason
  (a timeout, a missing element), the run fails.
- The day the bug is fixed, the test passes and the run **fails** with `XPASS(strict)`.
  That's the signal to remove the marker and close the bug.

Run only the bug tests:

```bash
uv run pytest -m bug -rx
```

**Severity:** Critical = login or purchase impossible for everyone · High = a core flow is
broken or gives wrong money values · Medium = wrong behavior with a workaround, or bad data
· Low = cosmetic.

## BUG-001

**Checkout is allowed with an empty cart, and places an empty order**

| | |
|---|---|
| Severity | Medium: creates orders with no items (bad data), no money is lost |
| User | `standard_user` (other users not checked) |
| Test | TC-CHECKOUT-008, `tests/ui/test_checkout.py::test_empty_cart_cannot_be_checked_out` |
| Found | Manually (David), then confirmed with a script on 2026-11-26 |

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
