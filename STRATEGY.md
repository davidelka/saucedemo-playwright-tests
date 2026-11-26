# Test strategy

Written as if Sauce Demo were a product my team owns. **Today:** 114 tests (73 UI, 41 unit
tests of the framework) covering the 100 cases in TEST_PLAN.md; 24 UI tests cover the 17
known bugs and run as expected failures. A push or pull request run takes about 2.5 minutes
in CI.

The rule throughout: **test each rule at the lowest layer that can catch it**, and keep UI
tests for what only a browser can show.

## What you would test at the unit, API and UI layers, and why

**Unit (in the application's repository).** The rules behind the screens: price, tax and
total calculation, including rounding and formatting; sort order; required fields and the
order of their messages; cart add and remove; login rules. They run in milliseconds, and a
failure points at one function. In this repository the unit layer tests the framework
itself: price parsing, the tax helper, config, automatic tags, the known-bug marker and the
traceability report.

**API.** Sauce Demo has no API: the session is a cookie and the cart is a list of product
IDs in localStorage. In a real shop, API tests would cover login and lockout, the catalog
and its prices, the cart stored per user, and orders: totals and tax computed on the
server, rejecting an empty cart (BUG-001 belongs here first), required fields, and placing
the same order twice. Contract tests would keep frontend and backend from drifting apart.
API tests are faster and steadier than UI tests, and the server is where money must be
right first. The API would also seed UI tests, so each starts at the point it tests; this
framework already does that for login, with a saved session.

**UI (this repository).** The main journeys end to end (log in, sort, cart, checkout with
the totals the user sees) and what only a browser shows: messages, navigation, behavior per
user type and differences between browsers. Here the UI also checks the tax math and every
validation message, because it is the only interface we have. In a real product most of
those checks would move down a layer.

## What you would deliberately not automate

- **Exploratory testing.** It is how the bugs in BUGS.md were found. A bug gets a test
  once it is known.
- **Full-page pixel comparison on every pull request.** Fonts differ between machines, so
  it is noisy; a few component screenshots in one Docker image, nightly, are enough.
- **Pages we don't own,** such as the footer's social links and the Sauce Labs site behind
  "About". At most, check the link's address.
- **Every combination through the UI.** All products × all fields × all users belongs in
  unit or API tests; the UI keeps one case per rule.
- **Load testing.** It needs its own tool (k6, Locust) and environment. The UI suite
  keeps only simple time budgets.
- **Judgment calls:** whether a layout looks right or wording is clear. Automated
  accessibility checks catch part of it; the rest needs a person.

## How you would scale this framework to 1,000+ tests and several contributors

Already in place: page objects and shared header and menu components, fixtures that hide
setup, test-case IDs with a traceability report, automatic tags, `--strict-markers`, lint,
format and type checks in CI, and a Docker image that runs the suite the same way on any
machine. Next:

- **More components.** Pages built from shared parts (product card, cart row, form), so
  each part changes in one place.
- **Fixture layers.** The root `conftest.py` keeps config, auth and browser fixtures; each
  feature folder gets its own `conftest.py` for its data.
- **Data builders.** Functions such as `a_customer(postal_code="")` that build valid data
  with overrides, unique per test, so parallel tests never share data.
- **Users through an API.** A saved session per user and worker works for six shared demo
  accounts; with a real backend, each worker creates its own user.
- **Sharding by duration.** xdist spreads tests over one machine's cores and the CI matrix
  over machines; split shards by recorded duration (pytest-split) so they finish together.
- **Ownership.** Each feature tag and folder belongs to one team, and CODEOWNERS makes that
  team review changes to it.
- **CI inside the Docker image** contributors use, so a CI failure reproduces on a laptop
  with the same browsers and fonts.
- **A report with history.** JUnit XML sent to Allure or ReportPortal shows trends, the
  slowest tests and each test's flake rate.

## Your policy for handling flaky tests

A flaky test passes and fails on the same code. It costs trust, so it is handled at once.

1. **Rerun once, and say so.** CI reruns a failed test once (`--reruns 1`). If it then
   passes, the job stays green, but the traceability report and job summary mark it
   "🔁 passed on rerun (flaky)". CI uploads `test-results/` whenever tests ran, not only
   when the job fails, so every flake comes with the trace of its failure.
2. **Fix it, or quarantine it.** The owning team reads the trace. If the fix isn't quick,
   the test is quarantined with an owner, a ticket and an expiry date: it runs nightly but
   doesn't block pull requests, and after the date it is fixed or deleted. (Not built yet:
   a `quarantine` marker that fails CI once its date has passed.)
3. **Never add sleeps.** A fixed wait hides the cause and slows every run. Wait for the
   condition instead, as `expect()` does throughout this framework.
4. **An intermittent product bug is a bug, not a flake.** It goes in BUGS.md.
5. **Find flakes before pull requests do:** the nightly run repeats each test three times
   (`--count 3`) in Chromium, Firefox and WebKit.

## How you would decide which tests run on every pull request versus nightly

By time budget and risk. A pull request run must be fast enough that people wait for it:
about 10 minutes at most. Slower or lower-risk checks run nightly.

**Every pull request:** lint, format and type checks, unit tests, the full UI suite on
Chromium and Firefox in parallel, and a smoke run inside the Docker image. That takes about
2.5 minutes, so there is no reason to run less.

**Once the suite outgrows 10 minutes,** a pull request runs smoke, all P1 cases (login and
purchase), and the tests tagged with the features the change touches. The full
cross-browser suite moves to the merge into `main`.

**Nightly** (03:00 UTC, the same `ci.yml`, or by hand with **nightly** ticked): everything
a pull request runs, plus WebKit, with every test run three times to catch flaky tests.
Slower checks join it as the suite grows. A nightly failure opens a ticket for the team
that owns the feature.
