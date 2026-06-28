#!/bin/bash
set -e

echo "Waiting for database..."
python /app/scripts/wait_for_db.py

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
