"""Automatic tags, so nobody has to remember to add them.

- Layer, from the folder a test lives in: ``tests/ui/...`` -> ``ui``.
- User, from the ``user`` a test runs as: ``problem_user`` -> ``user_problem``.
  Tests that use the ``user`` fixture without parametrizing it run as the default
  user and get that user's tag.

Hand-written tags (suite, feature, flow) stay on the tests themselves. All tags
are registered in pyproject.toml, so ``--strict-markers`` still catches typos.

Loaded as a pytest plugin via ``pytest_plugins = ["framework.tagging"]``.
"""

import pytest

from framework.data.users import DEFAULT_USER

LAYER_BY_DIR = {"unit": "unit", "ui": "ui", "visual": "visual"}
USER_PARAM = "user"
TESTS_DIR = "tests"


def user_marker(user: str) -> str:
    """``problem_user`` -> ``user_problem``."""
    return "user_" + str(user).removesuffix("_user")


def layer_of(item: pytest.Item, config: pytest.Config) -> str | None:
    try:
        relative = item.path.relative_to(config.rootpath / TESTS_DIR)
    except ValueError:
        return None
    return LAYER_BY_DIR.get(relative.parts[0]) if len(relative.parts) > 1 else None


def user_of(item: pytest.Item) -> str | None:
    if USER_PARAM not in getattr(item, "fixturenames", ()):
        return None
    callspec = getattr(item, "callspec", None)
    return str(callspec.params.get(USER_PARAM, DEFAULT_USER)) if callspec else str(DEFAULT_USER)


# tryfirst: tags must exist before pytest's own -m/-k deselection looks at them.
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if layer := layer_of(item, config):
            item.add_marker(layer)
        if user := user_of(item):
            item.add_marker(user_marker(user))
