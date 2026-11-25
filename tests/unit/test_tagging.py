"""Tests for automatic tags (framework/tagging.py)."""

import pytest

from framework.testcase import tc

pytestmark = pytest.mark.unit

PLAN = "| ID | Title | Priority | Tags | Status |\n|--|--|--|--|--|\n"


@pytest.fixture
def project(pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch) -> pytest.Pytester:
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    pytester.makefile(".md", TEST_PLAN=PLAN)
    pytester.makeconftest(
        """
        import pytest
        pytest_plugins = ["framework.testcase", "framework.tagging"]
        @pytest.fixture
        def user():
            return "standard_user"
        """
    )
    return pytester


@tc("TC-UNIT-009")
def test_layer_tag_comes_from_directory(project: pytest.Pytester) -> None:
    # Plain folders, not packages: a package named "tests" would clash with this
    # project's own, already imported "tests" package (pytester runs in-process).
    (project.path / "tests/ui").mkdir(parents=True)
    (project.path / "tests/unit").mkdir()
    (project.path / "tests/ui/test_a.py").write_text("def test_a(): pass\n")
    (project.path / "tests/unit/test_b.py").write_text("def test_b(): pass\n")
    project.runpytest("-m", "ui").assert_outcomes(passed=1, deselected=1)
    project.runpytest("-m", "unit").assert_outcomes(passed=1, deselected=1)


@tc("TC-UNIT-010")
def test_user_tag_comes_from_user_parameter_or_default(project: pytest.Pytester) -> None:
    project.makepyfile(
        test_x="""
        import pytest
        @pytest.mark.parametrize("user", ["standard_user", "problem_user"])
        def test_param(user): pass
        def test_default(user): pass
        def test_no_user(): pass
        """
    )
    project.runpytest("-m", "user_problem").assert_outcomes(passed=1, deselected=3)
    project.runpytest("-m", "user_standard").assert_outcomes(passed=2, deselected=2)
