"""Tests for the test-case ID plugin (framework/testcase.py).

Each test builds a throwaway project with ``pytester`` (its own TEST_PLAN.md
and conftest) and runs pytest inside it.
"""

from pathlib import Path

import pytest

from framework.testcase import load_test_plan, tc

pytestmark = pytest.mark.unit

PLAN = """\
| ID | Title | Priority | Tags | Status |
|----|-------|----------|------|--------|
| TC-A-001 | first | P1 | smoke | Automated |
| TC-A-002 | second | P2 | regression | Automated |
| TC-A-003 | manual one | P3 | - | Manual |
"""


@pytest.fixture
def project(pytester: pytest.Pytester) -> pytest.Pytester:
    pytester.makefile(".md", TEST_PLAN=PLAN)
    pytester.makeconftest('pytest_plugins = ["framework.testcase"]')
    return pytester


@tc("TC-UNIT-001")
def test_tc_rejects_malformed_id() -> None:
    with pytest.raises(ValueError, match="LOGIN-1"):
        tc("LOGIN-1")


@tc("TC-UNIT-002")
def test_load_test_plan_parses_rows(tmp_path: Path) -> None:
    plan = tmp_path / "TEST_PLAN.md"
    plan.write_text(PLAN)
    assert load_test_plan(plan) == {
        "TC-A-001": "Automated",
        "TC-A-002": "Automated",
        "TC-A-003": "Manual",
    }


@tc("TC-UNIT-003")
def test_collection_fails_without_id(project: pytest.Pytester) -> None:
    project.makepyfile(test_x="def test_no_id(): pass")
    result = project.runpytest()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "test_x.py::test_no_id" in result.stderr.str()
    assert "no test-case ID" in result.stderr.str()


@tc("TC-UNIT-004")
def test_collection_fails_on_unknown_id(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-999")
        def test_unknown(): pass
        """
    )
    result = project.runpytest()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "TC-A-999" in result.stderr.str()


@tc("TC-UNIT-005")
def test_collection_fails_on_duplicate_id(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-001")
        def test_one(): pass
        @tc("TC-A-001")
        def test_two(): pass
        """
    )
    result = project.runpytest()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "TC-A-001" in result.stderr.str()
    assert "test_two" in result.stderr.str()


@tc("TC-UNIT-006")
def test_collection_fails_on_non_automated_id(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-003")
        def test_manual(): pass
        """
    )
    result = project.runpytest()
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "TC-A-003" in result.stderr.str()


@tc("TC-UNIT-007")
def test_parametrized_cases_each_carry_an_id(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        import pytest
        from framework.testcase import tc
        @pytest.mark.parametrize("n", [
            pytest.param(1, marks=tc("TC-A-001")),
            pytest.param(2, marks=tc("TC-A-002")),
        ])
        def test_param(n): pass
        """
    )
    project.runpytest().assert_outcomes(passed=2)


@tc("TC-UNIT-008")
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
    project.runpytest("--tc", "TC-A-001").assert_outcomes(passed=1, deselected=1)


@tc("TC-UNIT-009")
def test_check_test_plan_flags_unautomated_rows(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.testcase import tc
        @tc("TC-A-001")
        def test_one(): pass
        """
    )
    result = project.runpytest("--check-test-plan")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert "TC-A-002" in result.stderr.str()
