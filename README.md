# Sauce Demo test framework (Playwright + pytest)

[![CI](https://github.com/davidelka/saucedemo-playwright-tests/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/davidelka/saucedemo-playwright-tests/actions/workflows/ci.yml?query=branch%3Amain)

UI tests for [Sauce Demo](https://www.saucedemo.com), a public practice store, written in
Python with Playwright (sync API, through pytest-playwright).

- **Core flows:** login, sorting, cart, checkout totals and checkout validation, and the
  side menu (logout, About, Reset App State).
- **Performance (bonus):** pages that show the product list must appear within 2 seconds;
  for `performance_glitch_user` the page freezes for 5 (see [below](#bonus-performance)).
- **Known bugs:** bugs of `problem_user`, `error_user`, `visual_user`,
  `performance_glitch_user` and `standard_user` are tests that are expected to fail, each linked to a report in [BUGS.md](BUGS.md).
- **CI:** GitHub Actions runs the suite on Chromium and Firefox in parallel, and every night
  on WebKit too, with each test run three times. Each run keeps an HTML report, a
  traceability report and the traces of failed tests.

Other documents: [TEST_PLAN.md](TEST_PLAN.md) (every test case and its ID),
[BUGS.md](BUGS.md) (bug reports), [STRATEGY.md](STRATEGY.md) (test strategy).

CI runs (newest first, each with its reports and traces): [GitHub Actions](https://github.com/davidelka/saucedemo-playwright-tests/actions/workflows/ci.yml?query=branch%3Amain)

## Setup

You need Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked
```

```bash
uv run playwright install
```

```bash
cp .env.example .env
```

- `uv sync --locked` installs the exact versions from `uv.lock` into `.venv`.
- `playwright install` downloads the browsers. On a fresh Linux machine add `--with-deps`
  to also install the system libraries they need (CI does this).
- `.env` holds `SAUCE_BASE_URL` and `SAUCE_PASSWORD` (and, optionally,
  `SAUCE_PAGE_BUDGET_SECONDS`). The password is the public demo
  password shown on the login page. The code has no default for it: if it is missing,
  every browser test errors at setup with a validation error that names `password`
  (unit tests still run).

## Running the tests

```bash
uv run pytest -n auto
```

This runs everything in Chromium, headless, with one worker process per logical CPU.

| To run | Command |
|---|---|
| Smoke tests (critical path) | `uv run pytest -m smoke` |
| Regression (all UI tests) | `uv run pytest -m regression` |
| Known-bug tests, with each bug's reason | `uv run pytest -m bug -rx` |
| One feature | `uv run pytest -m login` (also `inventory`, `cart`, `checkout`, `menu`) |
| Positive or negative cases | `uv run pytest -m happy` or `-m negative` |
| Response-time checks | `uv run pytest -m performance` |
| One user | `uv run pytest -m user_problem` (also `user_standard`, `user_error`, …) |
| Browser tests only | `uv run pytest -m ui` |
| Framework unit tests (no browser) | `uv run pytest -m unit` |
| Combined tags | `uv run pytest -m "checkout and not bug"` |
| By test-case ID | `uv run pytest --tc TC-LOGIN-001,TC-CART-001` |
| In Firefox | `uv run pytest --browser firefox` |
| In both browsers | `uv run pytest --browser chromium --browser firefox` |
| With a visible browser | `uv run pytest --headed --tc TC-CHECKOUT-001` |
| In parallel | add `-n auto` to any command |
| Three times each (to find flaky tests) | `uv run pytest -n auto --count 3` |
| Without TEST_PLAN.md | add `--no-test-plan` (no plan is read, no traceability report is written) |

All tags are listed in `pyproject.toml` under `markers`. Because of `--strict-markers`, a
misspelled tag is an error, both on a test and after `-m` (pytest stops with "Unknown
marker(s) in '-m' expression"). Login-form tests don't use the `user` fixture, so they get
no automatic user tag; the locked-out case (TC-LOGIN-004) has `user_locked_out` set by hand.

Code checks (CI runs the same):

```bash
uv run ruff check .
```

```bash
uv run ruff format --check .
```

```bash
uv run mypy framework tests
```

## Run in Docker

The same suite without installing Python, uv or browsers: only Docker. The image is the
official Playwright image for the Playwright version in `uv.lock` (Chromium, Firefox and
WebKit included), with the locked dependencies installed.

```bash
docker compose build
```

```bash
mkdir -p reports test-results
```

```bash
docker compose run --rm tests
```

That runs the whole suite in Chromium with `-n auto`. Anything after `tests` goes to
pytest:

| To run | Command |
|---|---|
| Smoke tests | `docker compose run --rm tests -m smoke` |
| All three browsers | `docker compose run --rm tests --browser chromium --browser firefox --browser webkit` |
| One test case | `docker compose run --rm tests --tc TC-CHECKOUT-001` |
| On one worker | `docker compose run --rm tests -n 0` |

- **The password** comes from `.env` or your shell, never from the image. Without it,
  Compose stops before starting: "set SAUCE_PASSWORD in .env or your shell".
- **Reports and traces** land in `reports/` and `test-results/` on your machine. The
  container runs as user 1000, so the files are yours. Create the two folders first: if
  Docker has to create them, they belong to root and the container can't write to them.
  If your user ID isn't 1000: `docker compose run --rm --user "$(id -u):$(id -g)" tests`.
- **Rebuilding is fast.** The dependencies have their own layer, so after a code change
  the rebuild takes about a second; only a change to `pyproject.toml` or `uv.lock`
  reinstalls them. The first build downloads the 2.9 GB image (about 3 minutes here).
- **One Playwright version.** The image's browsers are built for one Playwright version,
  so TC-CFG-003 fails if the Dockerfile and `uv.lock` name different versions.
- The full suite in all three browsers takes about 2.5 minutes in the container on a
  4-core, 8-thread laptop.

## Reports and debugging

**HTML report.** Add `--html` to write one self-contained file:

```bash
uv run pytest -n auto --html reports/report.html --self-contained-html
```

It has a **Test ID** column. For a failed test it shows the screenshot and a link to the
trace.

**Traceability report.** Every run writes `reports/traceability.md`. It lists each case in
`TEST_PLAN.md` with its result (passed, failed, expected failure, passed on rerun, skipped
or not run) and the tests that ran it. It also lists tests without an ID and IDs that are
not in the plan. A missing or unknown ID is listed, not treated as a failure. In CI the
same report is shown on the job's summary page.

**Traces and screenshots.** `pyproject.toml` sets
`--tracing=retain-on-failure --screenshot=only-on-failure --output=test-results` for every
run. A failed test leaves `test-results/<test name>/trace.zip` and `test-failed-1.png`. If a
rerun follows, it gets its own folder with `-retry1` at the end. Open a trace with:

```bash
uv run playwright show-trace test-results/<test name>/trace.zip
```

The trace viewer shows each action with the page before and after it, plus the console
and network log. You can also drop the file on https://trace.playwright.dev.

## CI

The workflow is `.github/workflows/ci.yml`. It runs on a push to `main`, on every pull
request, every night at 03:00 UTC (on `main`), and from the "Run workflow" button. A newer
push to the same branch cancels the run still in progress. Nightly runs are grouped
separately, so a push never cancels a nightly run, and a nightly run never cancels a push.

| Job | What it does |
|---|---|
| **Lint, types, unit tests** | `ruff check`, `ruff format --check`, `mypy`, then the unit tests (no browser) |
| **Tests (chromium)** and **Tests (firefox)** | Starts after the first job passes. A matrix runs one job per browser, in parallel; one failing does not cancel the others. Installs the browser (cached), then runs the whole suite with `-n auto` and one rerun for failed tests (`--reruns 1`). |
| **Docker (smoke)** | Starts after the first job passes. Builds the image from the `Dockerfile` and runs the unit and smoke tests inside it, so a broken image fails the run. |

**Nightly run.** The scheduled run adds a **Tests (webkit)** job and runs each test three
times (`--count 3`, pytest-repeat), still with one rerun. Each browser job may take 30
minutes instead of 15. To start one by hand on any branch, tick **nightly** under "Run
workflow", or:

```bash
gh workflow run ci.yml --ref <branch> -f nightly=true
```

Artifacts, per browser, kept for 14 days:

| Artifact | Contents | Uploaded |
|---|---|---|
| `report-<browser>` | HTML report and `traceability.md` | always |
| `traces-<browser>` | `test-results/`: the trace and screenshot of every failed attempt, including a test that then passed on its rerun | unless the run was cancelled; no artifact when nothing failed |

Because traces are uploaded even when the job passes, a flaky test (shown as "passed on
rerun" in the traceability report) still has the trace of the attempt that failed.

The password comes from the repository secret `SAUCE_PASSWORD`, not from the code. GitHub
masks secrets, so the job log shows `SAUCE_PASSWORD: ***`.

## Project structure

```
framework/                  reusable code, no tests
  config.py                 settings from SAUCE_* environment variables or .env
  auth.py                   log a user in once and save the session (storage state)
  bugs.py                   xfail_bug() and bug_symptom(): known bugs linked to BUGS.md
  money.py                  parse_price() and expected_tax(), with Decimal
  flows.py                  steps that span pages (start_checkout)
  tagging.py                pytest plugin: adds layer and user tags automatically
  timing.py                 seconds_until(): how long an action takes to show a page
  testcase.py               pytest plugin: tc() IDs, --tc, traceability report
  components/               header.py (cart link and badge), menu.py (side menu),
                            product_item.py
  pages/                    page objects: login, inventory, product, cart, checkout
  data/                     users, expected catalog, checkout customer
tests/
  conftest.py               fixtures: settings, auth_state, logged_in_page, page objects
  ui/                       browser tests, one file per feature
  unit/                     tests of the framework itself, no browser
TEST_PLAN.md                every test case: ID, title, priority, tags, status
BUGS.md                     bug reports
STRATEGY.md                 test strategy
pyproject.toml              dependencies, pytest options and tags, ruff, mypy
.github/workflows/ci.yml    CI pipeline
Dockerfile                  the test image: official Playwright image + locked dependencies
compose.yaml                docker compose run --rm tests: password, output folders, user
.dockerignore               what the image never sees (.env, outputs, local notes)
```

## Key design decisions

**Page objects, plus a header component.** Each page object holds its locators and actions
and returns plain values read from the page. For example, `InventoryPage.products()`
returns `Product(name, price)` objects and `CartPage.items()` returns `CartItem(name,
price, quantity)`. Tests compare those values. The header (cart link and badge) appears on
most pages after login, so it is one `Header` class that the inventory, product, cart and
order-complete page objects own (`inventory_page.header.cart_badge`). Most locators use Sauce
Demo's `data-test` attributes through `get_by_test_id`; `tests/conftest.py` points
Playwright at that attribute. The Add to cart and Remove buttons are found by role and name
inside their product card. *Why:* when the page changes, one file changes, and tests read
like the steps of a test case. `data-test` attributes don't change when text or styling
does.

**Fixtures provide everything.** A test asks for what it needs by name, for example
`inventory_page` or `cart_page`, and pytest builds it. All page-object fixtures in one test,
except `login_page`, share the same logged-in page, so `inventory_page` and `cart_page` drive the same tab.
pytest-playwright creates each browser context, records the trace, and closes the context
after the test. *Why:* setup and cleanup live in one place (`tests/conftest.py`), and every
test starts from a fresh browser context, so tests don't share a cart and can run in any
order or in parallel.

**Log in once, reuse the session.** Only the login tests fill in the login form as part of
the test. For every other test, the `auth_state` fixture logs the user in once through the UI and saves the
session (cookies and localStorage) to a JSON file. `logged_in_page` opens a new context
from that file, so the test starts already logged in. This happens once per user, per
xdist worker and per browser: each worker is its own pytest session with its own temporary
folder, so two processes never write the same file. Sauce Demo's session cookie expires
after 10 minutes, so a file older than 5 minutes is re-created (tested by TC-AUTH-006).
*Why:* logging in through the form before every test is slow and tests the same thing
again and again.

**Expected values come from the page, with one pinned catalog test.** Sorting, cart and
checkout tests read names and prices from the product list, then compute the expected
order, cart contents or totals. Only TC-INV-001 compares the product list with a fixed
catalog (`framework/data/products.py`). *Why:* a new or repriced product breaks one test,
not twenty, and that test's failure says exactly what changed. The trade-off: if the
product list itself showed a wrong price, the cart tests would agree with it. TC-INV-001
is the test that catches that.

**Money is `Decimal`, tax is rounded half-up.** `parse_price` turns `"$29.99"` or
`"Item total: $29.99"` into `Decimal("29.99")`. `expected_tax` is 8% of the item total,
rounded to the cent with `ROUND_HALF_UP`. *Why:* a float can't hold 15.99 exactly, so sums
can drift. Python's `round()` and `Decimal`'s default both round half to even
(0.125 → 0.12), which is not how shops round money; half-up is written down explicitly.
`parse_price` matches the whole label and keeps every digit shown: `"$89.8"` is 89.8 and
`"$105.96000000000001"` stays as it is, so a wrongly shown price fails the comparison
instead of being rounded into a pass. Text that isn't a price (`"-$5.00"`, `"$1,299.00"`)
raises an error.

**Known bugs are strict expected failures, most with a control case.** `xfail_bug("BUG-005",
"…")` (in `framework/bugs.py`) is `pytest.mark.xfail` with `strict=True`,
`raises=BugSymptom` and a reason that links to BUGS.md. `strict=True`: when the bug is
fixed the test passes, and the run fails with `XPASS(strict)`, so the marker gets removed
(`xfail_strict = true` in `pyproject.toml` makes every other xfail strict too).
`raises=BugSymptom`: only the bug's own check counts. Each bug test wraps that one check in
`with bug_symptom():`, which re-raises a failure there as `BugSymptom`. A failure before
it (a page that didn't load, a setup step) stays a plain `AssertionError` or
`TimeoutError` and fails the run. That matters because a failed `expect(...)` also raises
`AssertionError`: without the block, a broken setup step would be reported as the known
bug. A bug test without the block can never be an expected failure, so a forgotten block
shows up as a red run. Bug tests that run as several users also run as `standard_user`,
where the same check must pass. That proves the test checks the right thing. (BUG-001 is a
`standard_user` bug, so its test has no control case.)
*Why:* a known bug shouldn't turn CI red every day, but an expected failure must never hide
a broken test or a fixed bug.

**Test-case IDs and a traceability report.** Every test, or each case of a parametrized
test, has one `@tc("TC-<AREA>-<NNN>")` mark that matches a row in TEST_PLAN.md. After the
run, `framework/testcase.py` writes `reports/traceability.md`. When one ID runs several
times (in two browsers, say), the worst result wins. *Why:* anyone can see which planned
cases passed without reading code, run a case by its ID (`--tc`), and spot a test that has
no ID. The report works with xdist: results from all workers are collected in the main
process.

**Automatic tags.** `framework/tagging.py` adds two kinds of tag at collection time. The
layer tag comes from the folder (`tests/ui/` → `ui`, `tests/unit/` → `unit`). The user tag
comes from the `user` a test runs as (`problem_user` → `user_problem`; tests that start
logged in without choosing a user get `user_standard`). Suite (`smoke`, `regression`), feature, flow (`happy`,
`negative`) and `bug` tags are written on the tests. *Why:* tags that can be derived are
never forgotten or wrong.

**Configuration.** `framework/config.py` reads `SAUCE_*` environment variables or `.env`
with pydantic-settings. The password is a `SecretStr`, so it shows as `**********` if
settings are printed. *Why:* the same code runs locally and in CI, and no secret is in the
repository.

## Playwright TypeScript → this project

The assignment's examples use Playwright Test (TypeScript). These are the equivalents used
here.

| Playwright Test (TypeScript) | Here (pytest) |
|---|---|
| `test.fail()` | `xfail_bug(...)`: `pytest.mark.xfail(strict=True, raises=BugSymptom)`, with the bug check inside `bug_symptom()` |
| Setup project + `storageState` | `auth_state` fixture + `new_context(storage_state=...)` in `logged_in_page` |
| `projects` (one per browser) | `--browser chromium --browser firefox`; in CI, a matrix job per browser |
| `trace: 'retain-on-failure'` | `--tracing=retain-on-failure` (in `addopts`, `pyproject.toml`) |
| `screenshot: 'only-on-failure'` | `--screenshot=only-on-failure` (same place) |
| `retries: 1` | `--reruns 1` (pytest-rerunfailures) |
| `workers` | `-n auto` (pytest-xdist) |
| `--repeat-each 3` | `--count 3` (pytest-repeat) |
| `test.extend()` fixtures | pytest fixtures in `tests/conftest.py` |
| Tags + `--grep @smoke` | markers + `-m smoke` |
| `use: { testIdAttribute: 'data-test' }` | `playwright.selectors.set_test_id_attribute("data-test")` |
| `use: { baseURL }` | `base_url` fixture: `--base-url`, else `SAUCE_BASE_URL` |
| HTML reporter | pytest-html: `--html reports/report.html --self-contained-html` |

## Assumptions

- **Tax is 8% of the item total, rounded to the cent, half a cent up.** The site doesn't
  state the rule; 8% matches the totals it shows. With 8% and whole-cent prices, a total
  can never land exactly on half a cent, so half-up and half-even give the same result on
  this site. Half-up is set explicitly so the rule still holds if the rate changes.
- **The password is public.** `secret_sauce` is printed on the login page and in the
  assignment. No code file contains it: `.env.example` has it as the documented value, and
  the code reads it from the environment with no default.
- **BUG-001 (checkout with an empty cart) is a judgment call.** The site lets you check out
  an empty cart and shows "Thank you for your order!". The assignment doesn't define this
  case; I treat an empty order as a bug. The test accepts either fix: a disabled Checkout
  button, or staying on the cart page.
- **Products with the same price have no defined order.** Two products cost $15.99, so the
  price-sort tests compare prices only, not names.
- **`standard_user` is the reference.** Each special user was compared with it action by
  action, and every difference that reproduces is reported as a bug, even when the demo
  builds it in on purpose (as for `performance_glitch_user`): in a real product it would be
  one.
- **Fields of only spaces count as empty (BUG-014).** The site rejects empty fields; I
  assume it means to reject blank ones too.
- **Money is shown in dollars and cents (BUG-013).** An item total of
  `$105.96000000000001` is a display bug, even though the amount is right to the cent.
- **A page should appear within 2 seconds.** The site states no target. Two seconds is at
  least ten times what `standard_user` needs and well under the 5-second freeze, and it is
  a setting (`SAUCE_PAGE_BUDGET_SECONDS`).

## Bonus: performance

`tests/ui/test_performance.py` times four actions that bring up the product list: logging
in, sorting, **Back to products** and **Continue Shopping**. Each is timed from the click
until the list is visible, and must take at most 2 seconds.

| User | Measured | Result |
|---|---|---|
| `standard_user` (control) | 0.07–0.19 s, also with 8 workers running | passes |
| `performance_glitch_user` | 5.05–5.36 s | expected failure, [BUG-017](BUGS.md#bug-017) |

```bash
uv run pytest -m performance
```

How it works:

- **No sleeps.** `seconds_until(action, shown)` (`framework/timing.py`) reads the clock,
  runs the action, and checks `shown.is_visible()` again and again until it is true. It
  doesn't use `expect()`: `expect()` retries at growing intervals (100, 250, 500, then
  1000 ms), so it can see a page up to a second after it appeared. Against a page made to
  answer after exactly 1.3 seconds, `expect()` was 0.53 s late and the loop 0.03–0.05 s.
- **The budget is a setting:** `page_budget_seconds`, 2.0 by default. A slower machine or
  environment raises it without a code change: `SAUCE_PAGE_BUDGET_SECONDS=3`. Two seconds
  is at least ten times what `standard_user` needs and well under the glitch's 5 seconds, so
  network noise doesn't make the tests flaky.
- **Only the budget is the bug.** The assertion `seconds <= budget` is the only thing
  inside `bug_symptom()`. If the page never appears (15 s), the test fails.
- **Why only the product list:** I timed every page for both users (the table in
  BUG-017). `performance_glitch_user` is slow exactly where the product list appears; the
  product page, the cart and the checkout steps are as fast as for `standard_user`.
- **What the delay is:** the page doesn't load slowly, it freezes. A recorder in the page
  saw no frame painted for 5 seconds right after the click, and the list was added only
  after that.

This checks one user-visible delay against a budget, measured from the test machine on the
live site. It isn't load testing (see STRATEGY.md).

## Known limitations and next steps

- **Runs against the live public site.** If Sauce Demo is down or changes, the run fails.
  One rerun absorbs short glitches, not outages.
- **The one-time login that creates a saved session has no trace.** It runs in its own
  context, outside pytest-playwright's tracing; if it fails, you get the error message only.
- **WebKit runs only nightly,** not on pull requests.
- **Not covered:** `visual_user`'s layout differences (no screenshot tests), and
  accessibility.

With more time, in this order:

1. **Screenshot tests for `visual_user`, in Docker.** Its remaining bugs are about layout
   (things out of place), which DOM checks can't see. The Docker image gives the fixed
   fonts and browsers that stable baselines need. Playwright for Python has no built-in
   screenshot assertion, so this needs a small comparison helper (Pillow and pixelmatch)
   with an option to update the baselines.
2. **CI jobs inside the Docker image.** That removes the browser install from every job
   (for WebKit, about 165 system packages), which would make WebKit cheap enough to run on
   every pull request, not only nightly.
3. **A quarantine marker with an owner and an expiry date,** so a flaky test leaves the
   pull-request gate without being forgotten (see STRATEGY.md).
4. **Accessibility checks with axe on the main pages.** Cheap to add, and they catch whole
   classes of problems (missing labels, low contrast) that functional tests never look at.
5. **A trace for the one-time login.** When the saved-session login fails, today there is
   only an error message; a trace would make it as easy to debug as any test.

## Use of AI

I used an AI coding assistant (Claude Code) while building this: to draft code, tests and
documents, and to review them. I made the design decisions, checked every change, ran the
suite locally and in CI, and can explain each part. Before writing code, I planned the work
with the assistant.
