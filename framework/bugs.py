"""Marking a test as hitting a known bug, linked to its entry in BUGS.md."""

import re

import pytest

BUG_ID_RE = re.compile(r"^BUG-\d{3}$")


def xfail_bug(bug_id: str, summary: str) -> pytest.MarkDecorator:
    """Expected failure for a known bug.

    - ``raises=AssertionError``: only a wrong answer from the app counts as the bug.
      A timeout or any other error is a broken test and still fails the run.
    - ``strict=True``: if the test passes, the bug is fixed and the run fails
      ("XPASS(strict)") so the marker gets removed.
    """
    if not BUG_ID_RE.match(bug_id):
        raise ValueError(f"bug id {bug_id!r} must look like BUG-001")
    return pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=f"{bug_id}: {summary} (see BUGS.md#{bug_id.lower()})",
    )
