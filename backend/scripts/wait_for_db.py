#!/usr/bin/env python3
"""Wait for PostgreSQL to become available before starting the application."""

import os
import sys
import time

import psycopg2


def wait_for_db(
    max_retries: int = 30,
    retry_interval: float = 2.0,
) -> None:
    """Block until PostgreSQL accepts connections."""
    database_url = os.environ.get("DATABASE_URL", "")
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(sync_url)
            conn.close()
            print(f"Database is ready (attempt {attempt})")
            return
        except psycopg2.OperationalError as exc:
            print(f"Waiting for database... attempt {attempt}/{max_retries}: {exc}")
            time.sleep(retry_interval)

    print("Database connection failed after maximum retries")
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()
