import os
import sys
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure the backend directory is on sys.path so that `app` can be imported
_backend_dir = str(Path(__file__).parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.core.config import Settings, get_settings
from app.database.base import Base
from app.database.session import dispose_engine, get_db, get_engine, get_session_factory
from app.main import create_app
from app.services.user import UserService


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test-specific settings."""
    return Settings(
        APP_ENV="testing",
        APP_NAME="LearnOS Test",
        DEBUG=True,
        LOG_LEVEL="WARNING",
        DATABASE_URL=os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+asyncpg://learnos:learnos@localhost:5432/learnos_test",
        ),
        TEST_DATABASE_URL=os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+asyncpg://learnos:learnos@localhost:5432/learnos_test",
        ),
        REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        JWT_SECRET_KEY="test-secret-key-for-testing-only",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        CORS_ORIGINS=["http://localhost:3000"],
    )


@pytest.fixture(autouse=True)
def reset_engine(test_settings: Settings) -> Generator[None, None, None]:
    """Reset database engine between tests."""
    import app.database.session as session_module

    session_module._engine = None
    session_module._session_factory = None
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def app(test_settings: Settings):
    """Create a test FastAPI application."""
    get_settings.cache_clear()
    with patch("app.core.config.get_settings", return_value=test_settings):
        with patch("app.database.session.get_settings", return_value=test_settings):
            with patch("app.database.redis.get_settings", return_value=test_settings):
                yield create_app(settings=test_settings)


async def _override_get_db() -> AsyncGenerator[AsyncMock, None]:
    """Provide a mock database session for tests."""
    session = AsyncMock()
    try:
        yield session
    finally:
        pass


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client with mocked dependencies."""
    app.dependency_overrides[get_db] = _override_get_db

    with (
        patch(
            "app.api.v1.router.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "app.api.v1.router.check_redis_connection",
            new_callable=AsyncMock,
            return_value=True,
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def db_session(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    """Provide a real database session for integration tests."""
    from sqlalchemy import text

    try:
        engine = get_engine(test_settings)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("Test database not available")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = get_session_factory(test_settings)
    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await dispose_engine()


@pytest.fixture
async def integration_client(
    app,
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client wired to a real test database session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_service() -> AsyncMock:
    """Provide a mocked UserService for API unit tests."""
    return AsyncMock(spec=UserService)


@pytest.fixture
def mock_playlist_service() -> AsyncMock:
    """Provide a mocked PlaylistService for API unit tests."""
    from app.services.playlist import PlaylistService

    return AsyncMock(spec=PlaylistService)
