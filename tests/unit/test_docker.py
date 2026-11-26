"""The Docker image must use the same Playwright version as uv.lock.

The image comes with browsers built for one Playwright version. If the Dockerfile and
uv.lock disagree, the Playwright package in the image can't find its browsers, so the
two must change together.
"""

import importlib.metadata
import re
from pathlib import Path

import pytest

from framework.testcase import tc

pytestmark = pytest.mark.unit

DOCKERFILE = Path(__file__).resolve().parents[2] / "Dockerfile"
IMAGE_VERSION = re.compile(r"^FROM mcr\.microsoft\.com/playwright/python:v(\d+\.\d+\.\d+)-", re.M)


@tc("TC-CFG-003")
def test_docker_image_matches_installed_playwright() -> None:
    assert DOCKERFILE.is_file(), "no Dockerfile at the repository root"
    match = IMAGE_VERSION.search(DOCKERFILE.read_text())
    assert match, "the Dockerfile has no FROM mcr.microsoft.com/playwright/python:vX.Y.Z-… line"
    installed = importlib.metadata.version("playwright")  # the version uv.lock installs
    assert match.group(1) == installed, (
        f"the Dockerfile uses Playwright {match.group(1)} but uv.lock installs {installed}: "
        "change both together"
    )
