# Build stage
FROM python:3.12-slim AS builder

ENV POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN /opt/poetry/bin/poetry install --no-root --only main

# Runtime stage
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser . .

RUN chmod +x /app/docker/entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker/entrypoint.sh"]
