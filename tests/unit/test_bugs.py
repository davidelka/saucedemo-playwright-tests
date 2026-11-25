"""Tests for the known-bug marker (framework/bugs.py).

A known bug is an expected failure only when the app gives the wrong answer (an
AssertionError). Anything else must still fail the run: a broken test, and the
bug being fixed (the test passes, so the marker has to come off).
"""

import pytest

from framework.bugs import xfail_bug
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
        from framework.bugs import xfail_bug
        @xfail_bug("BUG-001", "checkout is allowed with an empty cart")
        def test_bug(): assert False
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
        from framework.bugs import xfail_bug
        @xfail_bug("BUG-001", "x")
        def test_broken_test(): raise TimeoutError("locator never appeared")
        @xfail_bug("BUG-001", "x")
        def test_bug_fixed(): pass
        """
    )
    project.runpytest().assert_outcomes(failed=2)


@tc("TC-UNIT-018")
def test_xfail_bug_rejects_malformed_id() -> None:
    with pytest.raises(ValueError, match="BUG-1"):
        xfail_bug("BUG-1", "x")
