"""Tests for the response-time helper (framework/timing.py), with a stand-in for a Locator."""

import time

import pytest

from framework.testcase import tc
from framework.timing import seconds_until

pytestmark = pytest.mark.unit


class VisibleAfter:
    """Stands in for a Locator: ``is_visible()`` is False ``checks`` times, then True."""

    def __init__(self, checks: int) -> None:
        self.remaining = checks
        self.calls = 0

    def is_visible(self) -> bool:
        self.calls += 1
        self.remaining -= 1
        return self.remaining < 0


NEVER = 10**9


@tc("TC-UNIT-023")
def test_seconds_until_times_action_and_wait() -> None:
    shown = VisibleAfter(checks=3)
    seconds = seconds_until(lambda: time.sleep(0.05), shown)
    assert shown.calls == 4  # kept checking until it was visible, then stopped
    assert 0.05 <= seconds < 1  # the action's time counts


@tc("TC-UNIT-024")
def test_seconds_until_fails_if_never_visible() -> None:
    with pytest.raises(AssertionError, match="didn't appear within 0.05 s"):
        seconds_until(lambda: None, VisibleAfter(checks=NEVER), timeout_seconds=0.05)
