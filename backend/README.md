# LearnOS Backend

Production-ready FastAPI backend foundation for the LearnOS platform.

## Prerequisites

- Python 3.12
- Poetry
- Docker & Docker Compose

## Quick Start

```bash
# Copy environment file
cp ../.env.example ../.env

# Start all services
docker compose up --build

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Local Development (without Docker)

```bash
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

## Testing

```bash
poetry run pytest
poetry run pytest --cov=app
```

## Linting & Formatting

```bash
poetry run ruff check .
poetry run black --check .
poetry run isort --check .
```

## Project Structure

```
app/
├── api/v1/          # API routes (thin controllers)
├── core/            # Config, security, logging
├── database/        # SQLAlchemy engine, session, base models
├── models/          # Persistence models
├── schemas/         # Pydantic request/response schemas
├── repositories/    # Database access layer
├── services/        # Business logic layer
├── dependencies/    # FastAPI dependency injection
├── middleware/      # Cross-cutting concerns
├── exceptions/      # Custom exceptions and handlers
└── utils/           # Shared utilities
```
