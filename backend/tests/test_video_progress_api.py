"""Tests for the video progress API routes.

Tests cover:
- PATCH /videos/{video_id}/progress — Update progress
- GET /videos/{video_id}/progress — Get progress
- GET /playlists/{playlist_id}/progress — Get playlist summary
- GET /users/me/progress — Get all user progress
- Edge cases: unauthorized access, missing records, validation
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.core.config import Settings
from app.database.session import get_db
from app.models.enums import VideoProgressStatus
from app.models.video_progress import VideoProgress
from app.schemas.progress import ProgressResponseSchema, ProgressSummarySchema
from app.services.video_progress import VideoProgressService

TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
NOW = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        APP_ENV="testing",
        APP_NAME="LearnOS Test",
        DEBUG=True,
        LOG_LEVEL="WARNING",
        DATABASE_URL="postgresql+asyncpg://learnos:learnos@localhost:5432/learnos_test",
        TEST_DATABASE_URL="postgresql+asyncpg://learnos:learnos@localhost:5432/learnos_test",
        REDIS_URL="redis://localhost:6379/0",
        JWT_SECRET_KEY="test-secret-key-for-testing-only",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        CORS_ORIGINS=["http://localhost:3000"],
    )


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock(spec=VideoProgressService)


@pytest.fixture
def app(test_settings: Settings, mock_service: AsyncMock):
    """Create a test app with mocked progress service."""
    from app.dependencies.video_progress import get_video_progress_service

    app = create_app(settings=test_settings)

    # Override the progress service dependency
    app.dependency_overrides[get_video_progress_service] = lambda: mock_service

    # Override the _get_current_user_id dependency to return test user
    from app.api.v1.progress import _get_current_user_id

    async def override_user_id():
        return TEST_USER_ID

    app.dependency_overrides[_get_current_user_id] = override_user_id

    return app


@pytest.fixture
async def client(app, mock_service: AsyncMock) -> AsyncClient:
    """Provide an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── PATCH /videos/{video_id}/progress ──────────────────────────────────────


@pytest.mark.asyncio
async def test_update_progress_success(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test successful progress update."""
    video_id = uuid4()
    mock_service.update_progress.return_value = ProgressResponseSchema(
        id=uuid4(),
        user_id=TEST_USER_ID,
        video_id=video_id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
        created_at=NOW,
        updated_at=NOW,
    )

    response = await client.patch(
        f"/api/v1/videos/{video_id}/progress",
        json={
            "completion_percentage": 50.0,
            "last_position_seconds": 120,
            "watch_time_seconds": 120,
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["completion_percentage"] == 50.0
    assert data["last_position_seconds"] == 120


@pytest.mark.asyncio
async def test_update_progress_invalid_percentage(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test that completion_percentage > 100 is rejected."""
    video_id = uuid4()

    response = await client.patch(
        f"/api/v1/videos/{video_id}/progress",
        json={"completion_percentage": 150.0},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_progress_negative_position(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test that negative last_position_seconds is rejected."""
    video_id = uuid4()

    response = await client.patch(
        f"/api/v1/videos/{video_id}/progress",
        json={"last_position_seconds": -1},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_progress_video_not_found(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test update progress for non-existent video."""
    video_id = uuid4()
    from app.exceptions.base import NotFoundException
    mock_service.update_progress.side_effect = NotFoundException(message="Video not found")

    response = await client.patch(
        f"/api/v1/videos/{video_id}/progress",
        json={"last_position_seconds": 30},
    )

    assert response.status_code == 400


# ─── GET /videos/{video_id}/progress ────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_progress_success(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test successful progress retrieval."""
    video_id = uuid4()
    mock_service.get_progress.return_value = ProgressResponseSchema(
        id=uuid4(),
        user_id=TEST_USER_ID,
        video_id=video_id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
        created_at=NOW,
        updated_at=NOW,
    )

    response = await client.get(f"/api/v1/videos/{video_id}/progress")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["completion_percentage"] == 50.0


@pytest.mark.asyncio
async def test_get_progress_not_found(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test get progress for non-existent record."""
    video_id = uuid4()
    from app.exceptions.base import NotFoundException
    mock_service.get_progress.side_effect = NotFoundException(message="Progress record not found")

    response = await client.get(f"/api/v1/videos/{video_id}/progress")

    assert response.status_code == 404


# ─── GET /playlists/{playlist_id}/progress ──────────────────────────────────


@pytest.mark.asyncio
async def test_get_playlist_progress_success(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test successful playlist progress retrieval."""
    playlist_id = uuid4()
    mock_service.get_playlist_progress.return_value = ProgressSummarySchema(
        total_videos=5,
        completed_videos=2,
        in_progress_videos=1,
        not_started_videos=2,
        total_watch_time_seconds=1800,
        average_completion_percentage=40.0,
        estimated_remaining_seconds=7200,
    )

    response = await client.get(f"/api/v1/playlists/{playlist_id}/progress")

    assert response.status_code == 200
    data = response.json()
    assert data["total_videos"] == 5
    assert data["completed_videos"] == 2
    assert data["average_completion_percentage"] == 40.0


@pytest.mark.asyncio
async def test_get_playlist_progress_not_found(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test get playlist progress for non-existent playlist."""
    playlist_id = uuid4()
    from app.exceptions.base import NotFoundException
    mock_service.get_playlist_progress.side_effect = NotFoundException(message="Playlist not found")

    response = await client.get(f"/api/v1/playlists/{playlist_id}/progress")

    assert response.status_code == 404


# ─── GET /users/me/progress ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_progress_success(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test successful user progress retrieval."""
    mock_service.get_user_progress.return_value = [
        ProgressResponseSchema(
            id=uuid4(),
            user_id=TEST_USER_ID,
            video_id=uuid4(),
            status=VideoProgressStatus.IN_PROGRESS,
            completion_percentage=50.0,
            last_position_seconds=120,
            watch_time_seconds=120,
            created_at=NOW,
            updated_at=NOW,
        ),
        ProgressResponseSchema(
            id=uuid4(),
            user_id=TEST_USER_ID,
            video_id=uuid4(),
            status=VideoProgressStatus.COMPLETED,
            completion_percentage=100.0,
            last_position_seconds=300,
            watch_time_seconds=300,
            created_at=NOW,
            updated_at=NOW,
        ),
    ]

    response = await client.get("/api/v1/users/me/progress")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["status"] == "in_progress"
    assert data[1]["status"] == "completed"


@pytest.mark.asyncio
async def test_get_user_progress_empty(
    client: AsyncClient,
    mock_service: AsyncMock,
) -> None:
    """Test user progress returns empty list when no records exist."""
    mock_service.get_user_progress.return_value = []

    response = await client.get("/api/v1/users/me/progress")

    assert response.status_code == 200
    data = response.json()
    assert data == []


# ─── Schema Validation ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_progress_update_schema_validation() -> None:
    """Test Pydantic validation for ProgressUpdateSchema."""
    from app.schemas.progress import ProgressUpdateSchema

    # Valid schema
    schema = ProgressUpdateSchema(
        completion_percentage=75.0,
        last_position_seconds=180,
        watch_time_seconds=180,
    )
    assert schema.completion_percentage == 75.0
    assert schema.last_position_seconds == 180

    # Invalid: completion_percentage > 100
    with pytest.raises(Exception):
        ProgressUpdateSchema(completion_percentage=150.0)

    # Invalid: negative position
    with pytest.raises(Exception):
        ProgressUpdateSchema(last_position_seconds=-1)

    # Invalid: negative watch time
    with pytest.raises(Exception):
        ProgressUpdateSchema(watch_time_seconds=-10)


@pytest.mark.asyncio
async def test_progress_summary_schema() -> None:
    """Test ProgressSummarySchema creation."""
    from app.schemas.progress import ProgressSummarySchema

    schema = ProgressSummarySchema(
        total_videos=10,
        completed_videos=3,
        in_progress_videos=2,
        not_started_videos=5,
        total_watch_time_seconds=3600,
        average_completion_percentage=30.0,
        estimated_remaining_seconds=5400,
    )

    assert schema.total_videos == 10
    assert schema.completed_videos == 3
    assert schema.not_started_videos == 5
    assert schema.average_completion_percentage == 30.0