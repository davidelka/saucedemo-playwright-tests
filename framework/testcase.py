"""Test-case ID traceability between automated tests and ``TEST_PLAN.md``.

Every test carries exactly one ``@tc("TC-<AREA>-<NNN>")`` mark, and every ID must
be a row in TEST_PLAN.md whose status is ``Automated``. Collection stops with a
usage error that lists every problem at once, so the plan and the code can't drift.

Loaded as a pytest plugin via ``pytest_plugins = ["framework.testcase"]``.
"""

import re
from pathlib import Path
from typing import Any

import pytest

TEST_ID_RE = re.compile(r"^TC-[A-Z]+-\d{3}$")
PLAN_ROW_RE = re.compile(r"^\|\s*(TC-[A-Z]+-\d{3})\s*\|(.*)\|\s*$")
PLAN_FILE = "TEST_PLAN.md"
AUTOMATED = "Automated"
# pytest-playwright runs the same test once per browser; those runs share an ID.
BROWSER_PARAM = "browser_name"


def tc(test_id: str) -> pytest.MarkDecorator:
    """Mark a test (or a ``pytest.param``) with its TEST_PLAN.md ID."""
    if not TEST_ID_RE.match(test_id):
        raise ValueError(f"Malformed test-case ID {test_id!r}, expected TC-<AREA>-<NNN>")
    return pytest.mark.tc(test_id)


def load_test_plan(path: Path) -> dict[str, str]:
    """Return ``{test_id: status}`` from the Markdown tables in TEST_PLAN.md."""
    plan: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PLAN_ROW_RE.match(line.strip())
        if not match:
            continue
        test_id, rest = match.groups()
        if test_id in plan:
            raise ValueError(f"{path.name}: duplicate row for {test_id}")
        plan[test_id] = rest.split("|")[-1].strip()
    return plan


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("test-plan", "test-case ID traceability")
    group.addoption(
        "--tc",
        action="store",
        default=None,
        metavar="ID[,ID...]",
        help="Run only tests with these TEST_PLAN.md IDs.",
    )
    group.addoption(
        "--check-test-plan",
        action="store_true",
        default=False,
        help="Also fail if an 'Automated' plan row has no collected test.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "tc(id): test-case ID from TEST_PLAN.md")


def _case_key(item: pytest.Item) -> tuple[Any, ...]:
    """Identify a test case independent of which browser it runs in."""
    callspec = getattr(item, "callspec", None)
    params = (
        tuple(sorted((k, repr(v)) for k, v in callspec.params.items() if k != BROWSER_PARAM))
        if callspec
        else ()
    )
    return (str(item.path), getattr(item, "originalname", item.name), params)


def _test_id(item: pytest.Item) -> str | None:
    marks = list(item.iter_markers("tc"))
    return marks[0].args[0] if len(marks) == 1 else None


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    plan_path = config.rootpath / PLAN_FILE
    if not plan_path.exists():
        raise pytest.UsageError(f"{PLAN_FILE} not found at {plan_path}")
    plan = load_test_plan(plan_path)

    problems: list[str] = []
    owner: dict[str, tuple[tuple[Any, ...], str]] = {}  # id -> (case key, first nodeid)
    for item in items:
        marks = list(item.iter_markers("tc"))
        if not marks:
            problems.append(f"{item.nodeid}: no test-case ID (add @tc('TC-...'))")
            continue
        if len(marks) > 1:
            ids = ", ".join(m.args[0] for m in marks)
            problems.append(f"{item.nodeid}: more than one test-case ID ({ids})")
            continue
        test_id = marks[0].args[0]
        item.user_properties.append(("test_id", test_id))
        if test_id not in plan:
            problems.append(f"{item.nodeid}: {test_id} is not in {PLAN_FILE}")
        elif plan[test_id] != AUTOMATED:
            problems.append(
                f"{item.nodeid}: {test_id} has status {plan[test_id]!r} in {PLAN_FILE}, "
                f"expected {AUTOMATED!r}"
            )
        key = _case_key(item)
        if test_id in owner and owner[test_id][0] != key:
            problems.append(f"{item.nodeid}: {test_id} is already used by {owner[test_id][1]}")
        owner.setdefault(test_id, (key, item.nodeid))

    if config.getoption("check_test_plan"):
        for test_id, status in plan.items():
            if status == AUTOMATED and test_id not in owner:
                problems.append(f"{PLAN_FILE}: {test_id} is 'Automated' but no test has it")

    if problems:
        raise pytest.UsageError(
            "Test-case ID problems:\n" + "\n".join(f"  - {p}" for p in problems)
        )

    selected_ids = config.getoption("tc")
    if selected_ids:
        wanted = {s.strip() for s in selected_ids.split(",") if s.strip()}
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
    test_id = dict(report.user_properties).get("test_id", "")
    cells.insert(1, f"<td>{test_id}</td>")
