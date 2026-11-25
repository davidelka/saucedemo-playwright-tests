"""Tests for test-case IDs and the post-run traceability report (framework/testcase.py).

Each report test builds a throwaway project with ``pytester`` (its own
TEST_PLAN.md and conftest), runs pytest inside it, and reads the report it wrote.
"""

from pathlib import Path

import pytest

from framework.testcase import PlanRow, load_test_plan, tc

pytestmark = pytest.mark.unit

PLAN = """\
| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-A-001 | first | P1 | smoke | Automated |
| TC-A-002 | second | P2 | regression | Automated |
| TC-A-003 | third | P2 | regression | Automated |
| TC-A-004 | manual one | P3 | - | Manual |
"""

REPORT = "trace.md"


@pytest.fixture
def project(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch) -> pytest.Pytester:
    # The inner run must not append to the real CI job summary.
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    # The inner runs share this process; pytest-playwright there would clash with
    # the outer session's ("nested soft assertion scopes"), and they need no browser.
    pytester.makeini("[pytest]\naddopts = -p no:playwright")
    pytester.makefile(".md", TEST_PLAN=PLAN)
    pytester.makeconftest('pytest_plugins = ["framework.testcase"]')
    return pytester


def run_and_read(project: pytest.Pytester, *args: str) -> tuple[pytest.RunResult, str]:
    result = project.runpytest(f"--traceability-report={REPORT}", *args)
    return result, (project.path / REPORT).read_text()


def row(report: str, test_id: str) -> str:
    """The report table row for one test-case ID."""
    return next(line for line in report.splitlines() if line.startswith(f"| {test_id} "))


@tc("TC-UNIT-001")
def test_tc_rejects_malformed_id() -> None:
    with pytest.raises(ValueError, match="LOGIN-1"):
        tc("LOGIN-1")


@tc("TC-UNIT-002")
def test_load_test_plan_parses_rows(tmp_path: Path) -> None:
    plan = tmp_path / "TEST_PLAN.md"
    plan.write_text(PLAN)
    rows = load_test_plan(plan)
    assert list(rows) == ["TC-A-001", "TC-A-002", "TC-A-003", "TC-A-004"]
    assert rows["TC-A-001"] == PlanRow("TC-A-001", "first", "Automated")
    assert rows["TC-A-004"].status == "Manual"


@tc("TC-UNIT-003")
def test_report_shows_passed_failed_and_not_run(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-001")
        def test_one(): pass
        @tc("TC-A-002")
        def test_two(): assert False
        """
    )
    result, report = run_and_read(project)
    result.assert_outcomes(passed=1, failed=1)
    assert "passed" in row(report, "TC-A-001")
    assert "test_x.py::test_one" in row(report, "TC-A-001")
    assert "FAILED" in row(report, "TC-A-002")
    assert "not run" in row(report, "TC-A-003")
    assert "Manual" in row(report, "TC-A-004")


@tc("TC-UNIT-004")
def test_report_shows_expected_failures_and_skips(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        import pytest
        from framework.testcase import tc
        @tc("TC-A-001")
        @pytest.mark.xfail(strict=True, reason="BUG-001")
        def test_known_bug(): assert False
        @tc("TC-A-002")
        @pytest.mark.skip(reason="not today")
        def test_skipped(): pass
        """
    )
    _, report = run_and_read(project)
    assert "expected failure" in row(report, "TC-A-001")
    assert "skipped" in row(report, "TC-A-002")


@tc("TC-UNIT-005")
def test_report_worst_outcome_wins_for_repeated_id(project: pytest.Pytester) -> None:
    # One ID that runs several times (per browser, per case) fails if any run fails.
    project.makepyfile(
        test_x="""
        import pytest
        from framework.testcase import tc
        @tc("TC-A-001")
        @pytest.mark.parametrize("n", [1, 2])
        def test_twice(n): assert n == 1
        @pytest.mark.parametrize("n", [
            pytest.param(1, marks=tc("TC-A-002")),
            pytest.param(2, marks=tc("TC-A-003")),
        ])
        def test_cases(n): pass
        """
    )
    _, report = run_and_read(project)
    assert "FAILED" in row(report, "TC-A-001")
    assert "test_twice[1]" in row(report, "TC-A-001")
    assert "test_twice[2]" in row(report, "TC-A-001")
    assert "passed" in row(report, "TC-A-002")
    assert "passed" in row(report, "TC-A-003")


@tc("TC-UNIT-006")
def test_report_lists_tests_without_id_and_unknown_ids(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        def test_no_id(): pass
        @tc("TC-A-999")
        def test_unknown(): pass
        """
    )
    result, report = run_and_read(project)
    result.assert_outcomes(passed=2)  # never blocks the run
    no_id, unknown = report.split("## Tests without a test-case ID")[1].split(
        "## IDs not in TEST_PLAN.md"
    )
    assert "test_x.py::test_no_id" in no_id
    assert "TC-A-999" in unknown
    assert "test_x.py::test_unknown" in unknown


@tc("TC-UNIT-007")
def test_tc_option_selects_by_id(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-001")
        def test_one(): pass
        @tc("TC-A-002")
        def test_two(): pass
        """
    )
    result, report = run_and_read(project, "--tc", "TC-A-001")
    result.assert_outcomes(passed=1, deselected=1)
    assert "passed" in row(report, "TC-A-001")
    assert "not run" in row(report, "TC-A-002")


@tc("TC-UNIT-008")
def test_report_collects_results_from_xdist_workers(
    project: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2]))
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-001")
        def test_one(): pass
        @tc("TC-A-002")
        def test_two(): assert False
        """
    )
    result = project.runpytest_subprocess(f"--traceability-report={REPORT}", "-n", "2")
    result.assert_outcomes(passed=1, failed=1)
    report = (project.path / REPORT).read_text()
    assert "passed" in row(report, "TC-A-001")
    assert "FAILED" in row(report, "TC-A-002")
