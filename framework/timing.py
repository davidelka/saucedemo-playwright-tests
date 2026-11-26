"""Response time: how long a person waits from an action until the next page is shown."""

import time
from collections.abc import Callable
from typing import Protocol

# Long enough that a slow page is measured (and then fails its budget), not cut off.
DEFAULT_TIMEOUT_SECONDS = 15.0


class Showable(Protocol):
    """Anything with ``is_visible()``: a Playwright Locator, or a stand-in in unit tests."""

    def is_visible(self) -> bool: ...


def seconds_until(
    action: Callable[[], None],
    shown: Showable,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> float:
    """Seconds from just before ``action`` until ``shown`` is visible.

    It checks ``is_visible()`` again and again, without pausing, instead of using
    ``expect()``: expect() retries at growing intervals (up to 1 s), so a page could be
    measured up to a second late. Checking in a loop measures to within about 50 ms.
    While the page is busy (performance_glitch_user's page freezes), each check simply
    waits for it.

    Raises AssertionError if ``shown`` isn't visible after ``timeout_seconds``: a page
    that never appears is a failure, not a slow page.
    """
    start = time.perf_counter()
    action()
    while not shown.is_visible():
        if time.perf_counter() - start > timeout_seconds:
            raise AssertionError(f"{shown} didn't appear within {timeout_seconds} s")
    return time.perf_counter() - start
