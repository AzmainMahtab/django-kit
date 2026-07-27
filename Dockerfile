# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies and uv.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
ENV PYTHONPATH=/app

# Copy dependency metadata and install dependencies first for better caching.
COPY pyproject.toml .python-version README.md ./
RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:${PATH}"

# Copy source code.
COPY backend ./backend
COPY docker ./docker

RUN chmod +x /app/docker/entrypoint.sh

WORKDIR /app/backend

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
# ASGI, not WSGI: the app serves both HTTP and WebSockets (see backend/core/asgi.py).
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.core.asgi:application"]

# Development target with dev dependencies and auto-reload server.
FROM base AS dev

WORKDIR /app
RUN uv sync --dev
ENV PATH="/app/.venv/bin:${PATH}"

WORKDIR /app/backend

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
