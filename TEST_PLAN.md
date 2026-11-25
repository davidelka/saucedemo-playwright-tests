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

**Status:** `Automated` = covered by a test in `tests/` · `Manual` = checked by hand,
see the notes · `Not automated` = deliberately left out, see STRATEGY.md.

**Priority:** P1 = blocks a purchase or login · P2 = core function degraded ·
P3 = minor or cosmetic.

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
