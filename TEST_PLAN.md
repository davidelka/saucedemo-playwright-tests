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
