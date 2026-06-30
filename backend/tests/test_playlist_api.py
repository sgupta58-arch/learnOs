from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.dependencies.auth import get_current_user_token
from app.dependencies.playlist import get_playlist_service
from app.schemas.playlist import PlaylistListResponseSchema, PlaylistResponseSchema

NOW = datetime.now(UTC)


@pytest.fixture
async def playlist_client(app, mock_playlist_service: AsyncMock):
    app.dependency_overrides[get_playlist_service] = lambda: mock_playlist_service
    app.dependency_overrides[get_current_user_token] = lambda: type(
        "Token",
        (),
        {"sub": str(uuid4())},
    )()
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_playlist_service
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_playlist_api(playlist_client) -> None:
    client, mock_service = playlist_client
    pl_id = uuid4()
    mock_service.create_playlist.return_value = PlaylistResponseSchema(
        id=pl_id,
        user_id=uuid4(),
        title="API PL",
        description=None,
        source_type="other",
        source_url=None,
        thumbnail_url=None,
        status="active",
        target_completion_date=None,
        created_at=NOW,
        updated_at=NOW,
    )

    response = await client.post(
        "/api/v1/playlists",
        json={"title": "API PL"},
    )
    assert response.status_code == 201
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_list_playlists_api(playlist_client) -> None:
    client, mock_service = playlist_client
    mock_service.list_playlists.return_value = PlaylistListResponseSchema(items=[], total=0, skip=0, limit=100)
    response = await client.get("/api/v1/playlists")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_create_playlist_validation_error(playlist_client) -> None:
    client, _ = playlist_client
    response = await client.post("/api/v1/playlists", json={})
    assert response.status_code == 422
