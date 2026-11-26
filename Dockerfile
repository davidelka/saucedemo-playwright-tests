# The test suite in a container: Python, the locked dependencies and Playwright's browsers.
# Run it with Docker Compose (see compose.yaml and the README):
#   docker compose run --rm tests
#
# The official Playwright image for the exact version in uv.lock: it comes with Chromium,
# Firefox, WebKit and their system libraries. TC-CFG-003 fails if the two versions differ.
FROM mcr.microsoft.com/playwright/python:v1.65.2-noble

# uv, pinned to the version used to write uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /usr/local/bin/uv

# The virtual environment lives outside /app, so mounting the source over /app doesn't
# hide it. uv uses the image's Python 3.12 and never downloads one.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app

# Dependencies first: this layer is rebuilt only when pyproject.toml or uv.lock changes.
# --no-dev: the container runs tests; linting (ruff, mypy) stays on the host and in CI.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

# Then the code. .dockerignore keeps out .env, reports, caches and local files.
COPY . .

# No password here: values set in a Dockerfile stay readable in the image's history.
# It comes from the environment when the container runs (compose.yaml).
# Arguments after the image name are added to these; a later -n (say -n 0) wins.
ENTRYPOINT ["pytest", "-n", "auto"]
