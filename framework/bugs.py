"""Marking a test as hitting a known bug, linked to its entry in BUGS.md."""

import re
from collections.abc import Iterator
from contextlib import contextmanager

import pytest

BUG_ID_RE = re.compile(r"^BUG-\d{3}$")


class BugSymptom(AssertionError):
    """The check a known-bug test exists for failed (not a step on the way to it)."""


@contextmanager
def bug_symptom() -> Iterator[None]:
    """Wrap the check that shows the bug. Only a failure in here counts as the bug.

    A failed step before it (the page never loaded, a precondition) stays an ordinary
    failure, even though Playwright's ``expect`` raises AssertionError too.
    """
    try:
        yield
    except AssertionError as error:
        raise BugSymptom(*error.args) from error


def xfail_bug(bug_id: str, summary: str) -> pytest.MarkDecorator:
    """Expected failure for a known bug.

    - ``raises=BugSymptom``: only a failure inside the test's ``bug_symptom()`` block
      counts as the bug. Anything else (a failed step before it, a timeout) is a
      broken test and still fails the run. A bug test with no ``bug_symptom()`` block
      can never be an expected failure, so a forgotten block shows up as a red run.
    - ``strict=True``: if the test passes, the bug is fixed and the run fails
      ("XPASS(strict)") so the marker gets removed.
    """
    if not BUG_ID_RE.match(bug_id):
        raise ValueError(f"bug id {bug_id!r} must look like BUG-001")
    return pytest.mark.xfail(
        strict=True,
        raises=BugSymptom,
        reason=f"{bug_id}: {summary} (see BUGS.md#{bug_id.lower()})",
    )
