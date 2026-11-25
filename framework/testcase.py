"""Test-case IDs and the post-run traceability report.

Each test carries one ``@tc("TC-<AREA>-<NNN>")`` mark linking it to a row in
``TEST_PLAN.md``. Nothing is checked before the run: you select what to run
(``-m``, ``-k``, ``--tc``), pytest runs it, and at the end this plugin compares
the plan with what actually happened and writes a Markdown report:
which plan cases passed, failed, or didn't run, plus tests that have no ID or
an ID the plan doesn't know.

Loaded as a pytest plugin via ``pytest_plugins = ["framework.testcase"]``.
"""

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest

TEST_ID_RE = re.compile(r"^TC-[A-Z]+-\d{3}$")
PLAN_ROW_RE = re.compile(r"^\|\s*(TC-[A-Z]+-\d{3})\s*\|(.*)\|\s*$")
PLAN_FILE = "TEST_PLAN.md"
AUTOMATED = "Automated"
DEFAULT_REPORT = "reports/traceability.md"
TEST_ID_PROPERTY = "test_id"

# When one ID runs several times (once per browser, or per parametrized case),
# the worst outcome wins. Earlier in this list = worse.
OUTCOME_SEVERITY = ["failed", "error", "passed", "xfailed", "skipped"]
OUTCOME_LABEL = {
    "failed": "❌ FAILED",
    "error": "❌ ERROR",
    "passed": "✅ passed",
    "xfailed": "🟡 expected failure (known bug)",
    "skipped": "⏭ skipped",
}
NOT_RUN = "⚪ not run"


@dataclass(frozen=True)
class PlanRow:
    test_id: str
    title: str
    status: str


def tc(test_id: str) -> pytest.MarkDecorator:
    """Mark a test (or a ``pytest.param``) with its TEST_PLAN.md ID."""
    if not TEST_ID_RE.match(test_id):
        raise ValueError(f"Malformed test-case ID {test_id!r}, expected TC-<AREA>-<NNN>")
    return pytest.mark.tc(test_id)


def load_test_plan(path: Path) -> dict[str, PlanRow]:
    """Read the ``| ID | Title | ... | Status |`` table rows of TEST_PLAN.md, in file order."""
    plan: dict[str, PlanRow] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PLAN_ROW_RE.match(line.strip())
        if not match:
            continue
        test_id, rest = match.groups()
        cells = [c.strip() for c in rest.split("|")]
        if test_id in plan:
            raise ValueError(f"{path.name}: duplicate row for {test_id}")
        plan[test_id] = PlanRow(test_id, title=cells[0], status=cells[-1])
    return plan


def outcome_of(report: pytest.TestReport) -> str | None:
    """The outcome one phase report decides for its test, or None if it decides nothing.

    A test produces three reports (setup, call, teardown). The call report carries
    the real result; setup/teardown only matter when they fail or skip.
    """
    if report.outcome == "rerun":  # pytest-rerunfailures: a later attempt follows
        return None
    xfailed = hasattr(report, "wasxfail")
    if report.when == "call":
        if xfailed:
            # An xpass in strict mode is reported as a plain failure by pytest.
            return "xfailed" if report.skipped else "passed"
        return report.outcome
    if report.failed:
        return "error"
    if report.skipped and report.when == "setup":
        return "xfailed" if xfailed else "skipped"
    return None


def worst(outcomes: Iterable[str]) -> str:
    return min(outcomes, key=OUTCOME_SEVERITY.index)


def build_report(plan: dict[str, PlanRow], results: dict[str, tuple[str | None, str]]) -> str:
    """Render the report. ``results`` maps nodeid -> (test-case ID or None, outcome)."""
    by_id: dict[str, list[tuple[str, str]]] = {}
    no_id: list[str] = []
    for nodeid, (test_id, outcome) in results.items():
        if test_id is None:
            no_id.append(nodeid)
        else:
            by_id.setdefault(test_id, []).append((nodeid, outcome))

    rows, counts = [], {label: 0 for label in [*OUTCOME_LABEL.values(), NOT_RUN]}
    for row in plan.values():
        runs = by_id.get(row.test_id, [])
        if runs:
            result = OUTCOME_LABEL[worst(o for _, o in runs)]
        elif row.status == AUTOMATED:
            result = NOT_RUN
        else:
            result = row.status  # Manual / Not automated: not expected to run
        if result in counts:
            counts[result] += 1
        tests = "<br>".join(f"`{nodeid}`" for nodeid, _ in runs) or "–"
        rows.append(f"| {row.test_id} | {row.title} | {result} | {tests} |")

    unknown = sorted((tid, n) for tid, runs in by_id.items() if tid not in plan for n, _ in runs)
    summary = " · ".join(f"{label}: {n}" for label, n in counts.items() if n)
    lines = [
        "# Traceability report",
        "",
        f"Generated {datetime.now():%Y-%m-%d %H:%M} against `{PLAN_FILE}` "
        f"({len(plan)} cases). {summary}",
        "",
        "| ID | Title | Result | Tests |",
        "|----|-------|--------|-------|",
        *rows,
        "",
        "## Tests without a test-case ID",
        "",
        *([f"- `{n}`" for n in sorted(no_id)] or ["None."]),
        "",
        f"## IDs not in {PLAN_FILE}",
        "",
        *([f"- {tid}: `{n}`" for tid, n in unknown] or ["None."]),
        "",
    ]
    return "\n".join(lines)


class TraceabilityReport:
    """Collects each test's ID and outcome during the run, writes the report at the end."""

    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.outcomes: dict[str, list[str]] = {}
        self.test_ids: dict[str, str | None] = {}
        self.written: Path | None = None

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        # Under xdist this runs on the controller with reports sent back by the
        # workers; user_properties travel with them.
        test_id = dict(report.user_properties).get(TEST_ID_PROPERTY)
        self.test_ids.setdefault(report.nodeid, str(test_id) if test_id else None)
        outcome = outcome_of(report)
        if outcome:
            self.outcomes.setdefault(report.nodeid, []).append(outcome)

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        path_option = self.config.getoption("traceability_report")
        if hasattr(self.config, "workerinput") or self.config.option.collectonly:
            return  # xdist worker, or nothing ran
        if not path_option:
            return
        plan_path = self.config.rootpath / PLAN_FILE
        if not plan_path.exists():
            return
        results = {
            nodeid: (self.test_ids.get(nodeid), worst(outcomes))
            for nodeid, outcomes in self.outcomes.items()
        }
        text = build_report(load_test_plan(plan_path), results)
        out = self.config.rootpath / path_option
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        self.written = out
        if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(text + "\n")

    def pytest_terminal_summary(self, terminalreporter: pytest.TerminalReporter) -> None:
        if self.written:
            terminalreporter.write_line(f"traceability report: {self.written}")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("test-plan", "test-case IDs and traceability report")
    group.addoption(
        "--tc",
        action="store",
        default=None,
        metavar="ID[,ID...]",
        help="Run only tests with these TEST_PLAN.md IDs.",
    )
    group.addoption(
        "--traceability-report",
        action="store",
        default=DEFAULT_REPORT,
        metavar="PATH",
        help=f"Where to write the plan-vs-results report (default {DEFAULT_REPORT}; "
        "empty to disable).",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tc(id): test-case ID from TEST_PLAN.md")
    config.pluginmanager.register(TraceabilityReport(config), "traceability-report")


def _test_id(item: pytest.Item) -> str | None:
    mark = item.get_closest_marker("tc")
    return mark.args[0] if mark else None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if test_id := _test_id(item):
            item.user_properties.append((TEST_ID_PROPERTY, test_id))

    selected = config.getoption("tc")
    if selected:
        wanted = {s.strip() for s in selected.split(",") if s.strip()}
        keep = [i for i in items if _test_id(i) in wanted]
        drop = [i for i in items if _test_id(i) not in wanted]
        if drop:
            config.hook.pytest_deselected(items=drop)
        items[:] = keep


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells: list[str]) -> None:
    cells.insert(1, "<th>Test ID</th>")


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_row(report: pytest.TestReport, cells: list[str]) -> None:
    test_id = dict(report.user_properties).get(TEST_ID_PROPERTY, "")
    cells.insert(1, f"<td>{test_id}</td>")
