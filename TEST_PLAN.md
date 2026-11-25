# Test Plan: Sauce Demo

Every automated test carries exactly one test-case ID from this file, set with
`@tc("TC-<AREA>-<NNN>")` (for parametrized tests, one ID per case via
`pytest.param(..., marks=tc(...))`). Pytest checks this mapping at collection time:

- a test with no ID, an ID that isn't listed here, or an ID whose status isn't
  `Automated` stops the run with a usage error;
- two different tests sharing one ID stop the run (running the same test in
  several browsers is fine);
- `--check-test-plan` also fails when an `Automated` row below has no test. CI runs it.

Run a single case or a few: `uv run pytest --tc TC-LOGIN-001` or
`uv run pytest --tc TC-CART-001,TC-CART-002`. The HTML report has a **Test ID** column.

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
| TC-UNIT-002 | TEST_PLAN.md rows are parsed into ID → status | P2 | unit | Automated |
| TC-UNIT-003 | Collection fails for a test without an ID | P2 | unit | Automated |
| TC-UNIT-004 | Collection fails for an ID not in the plan | P2 | unit | Automated |
| TC-UNIT-005 | Collection fails when two tests share an ID | P2 | unit | Automated |
| TC-UNIT-006 | Collection fails for an ID whose status isn't Automated | P3 | unit | Automated |
| TC-UNIT-007 | Each parametrized case can carry its own ID | P2 | unit | Automated |
| TC-UNIT-008 | `--tc` selects tests by ID | P3 | unit | Automated |
| TC-UNIT-009 | `--check-test-plan` flags Automated rows without a test | P3 | unit | Automated |
