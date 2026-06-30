from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.exceptions.base import ConflictException, ForbiddenException, NotFoundException
from app.models.enums import PlaylistStatus, SourceType
from app.models.playlist import Playlist
from app.schemas.playlist import PlaylistCreateSchema, PlaylistUpdateSchema
from app.services.playlist import PlaylistService

NOW = datetime.now(UTC)


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> PlaylistService:
    return PlaylistService(mock_repo)


@pytest.mark.asyncio
async def test_create_playlist_validates_title(service: PlaylistService, mock_repo: AsyncMock) -> None:
    mock_repo.create.return_value = Playlist(
        id=uuid4(),
        user_id=uuid4(),
        title="Created",
        source_type=SourceType.OTHER,
        status=PlaylistStatus.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
    )
    data = PlaylistCreateSchema(title="  Created  ")
    res = await service.create_playlist(uuid4(), data)
    mock_repo.create.assert_awaited_once()
    assert res.title == "Created"


@pytest.mark.asyncio
async def test_get_playlist_not_found(service: PlaylistService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundException):
        await service.get_playlist(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_get_playlist_forbidden(service: PlaylistService, mock_repo: AsyncMock) -> None:
    owner_id = uuid4()
    other_id = uuid4()
    pl = Playlist(
        id=uuid4(),
        user_id=owner_id,
        title="X",
        source_type=SourceType.OTHER,
        status=PlaylistStatus.ACTIVE,
    )
    mock_repo.get_by_id.return_value = pl
    with pytest.raises(ForbiddenException):
        await service.get_playlist(other_id, pl.id)


@pytest.mark.asyncio
async def test_update_playlist_validates_title(service: PlaylistService, mock_repo: AsyncMock) -> None:
    user_id = uuid4()
    pl = Playlist(
        id=uuid4(),
        user_id=user_id,
        title="Old",
        source_type=SourceType.OTHER,
        status=PlaylistStatus.ACTIVE,
    )
    mock_repo.get_by_id.return_value = pl
    mock_repo.update.return_value = pl

    with pytest.raises(ConflictException):
        await service.update_playlist(user_id, pl.id, PlaylistUpdateSchema(title="   "))


@pytest.mark.asyncio
async def test_create_playlist_rejects_blank_title(service: PlaylistService) -> None:
    with pytest.raises(ConflictException):
        await service.create_playlist(uuid4(), PlaylistCreateSchema(title="   "))


@pytest.mark.asyncio
async def test_delete_playlist_already_deleted(service: PlaylistService, mock_repo: AsyncMock) -> None:
    user_id = uuid4()
    deleted_playlist = Playlist(
        id=uuid4(),
        user_id=user_id,
        title="Deleted",
        source_type=SourceType.OTHER,
        status=PlaylistStatus.ACTIVE,
        deleted_at=datetime.now(UTC),
    )
    mock_repo.get_by_id.return_value = deleted_playlist

    with pytest.raises(ConflictException, match="already deleted"):
        await service.delete_playlist(user_id, deleted_playlist.id)
