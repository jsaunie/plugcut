# Plugcut API image. Portable across any container host (Render, Railway, Fly, Cloud Run).
# uv-based, Python 3.12 (pinned in .python-version / pyproject). Runs Alembic migrations
# on boot, then serves the ASGI app on $PORT.

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# uv: fast, reproducible installs from uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

WORKDIR /app

# 1) Dependencies first, for layer caching. No dev deps in the image.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Application code.
COPY . .
RUN uv sync --frozen --no-dev

# Schema is managed by Alembic in production, never auto-created.
ENV PLUGCUT_AUTO_CREATE_SCHEMA=false
EXPOSE 8000

# Migrate, then serve. $PORT is provided by the host (defaults to 8000 locally).
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
