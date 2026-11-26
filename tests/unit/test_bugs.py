"""Tests for the known-bug marker (framework/bugs.py).

A known bug is an expected failure only when the test's own bug check fails: the
check inside ``bug_symptom()``. Anything else must still fail the run: a failed
step on the way there, a timeout, and the bug being fixed (the test passes, so the
marker has to come off).
"""

import pytest

from framework.bugs import BugSymptom, bug_symptom, xfail_bug
from framework.testcase import tc

pytestmark = pytest.mark.unit


@pytest.fixture
def project(pytester: pytest.Pytester) -> pytest.Pytester:
    pytester.makeini("[pytest]\naddopts = -p no:playwright")  # no browser needed
    return pytester


@tc("TC-UNIT-016")
def test_wrong_result_is_expected_failure_linked_to_bugs_md(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.bugs import bug_symptom, xfail_bug
        @xfail_bug("BUG-001", "checkout is allowed with an empty cart")
        def test_bug():
            with bug_symptom():
                assert False
        """
    )
    result = project.runpytest("-rx")
    result.assert_outcomes(xfailed=1)
    result.stdout.fnmatch_lines(
        ["*BUG-001: checkout is allowed with an empty cart*BUGS.md#bug-001*"]
    )


@tc("TC-UNIT-017")
def test_broken_test_and_fixed_bug_fail_the_run(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        from framework.bugs import bug_symptom, xfail_bug
        @xfail_bug("BUG-001", "x")
        def test_timeout_in_bug_check():
            with bug_symptom():
                raise TimeoutError("locator never appeared")
        @xfail_bug("BUG-001", "x")
        def test_bug_fixed():
            with bug_symptom():
                pass
        """
    )
    project.runpytest().assert_outcomes(failed=2)


@tc("TC-UNIT-018")
def test_xfail_bug_rejects_malformed_id() -> None:
    with pytest.raises(ValueError, match="BUG-1"):
        xfail_bug("BUG-1", "x")


@tc("TC-UNIT-020")
def test_failed_step_before_bug_check_fails_the_run(project: pytest.Pytester) -> None:
    # A failed Playwright expect() raises AssertionError too, so this stands for
    # "the page never loaded" as well as a plain assert.
    project.makepyfile(
        test_x="""
        from framework.bugs import bug_symptom, xfail_bug
        @xfail_bug("BUG-001", "x")
        def test_precondition_fails():
            assert False, "precondition: the overview page loaded"
            with bug_symptom():
                assert False
        @xfail_bug("BUG-001", "x")
        def test_no_bug_check_at_all():
            assert False
        """
    )
    project.runpytest().assert_outcomes(failed=2)


@tc("TC-UNIT-021")
def test_bug_symptom_keeps_message_and_original_error() -> None:
    with pytest.raises(BugSymptom, match="badge shows 3") as caught, bug_symptom():
        raise AssertionError("badge shows 3, expected 6")
    assert isinstance(caught.value, AssertionError)  # still reads as an assertion failure
    assert type(caught.value.__cause__) is AssertionError  # the report shows the failing line
