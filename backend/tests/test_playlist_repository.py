import pytest

from app.models.user import User
from app.models.playlist import Playlist
from app.repositories.user import UserRepository
from app.repositories.playlist import PlaylistRepository


@pytest.mark.asyncio
async def test_create_and_get_playlist(db_session) -> None:
    user_repo = UserRepository(db_session)
    playlist_repo = PlaylistRepository(db_session)

    user = User(full_name="Repo User", email="repo@example.com", password_hash="h")
    created_user = await user_repo.create_user(user)

    pl = Playlist(user_id=created_user.id, title="My List")
    created = await playlist_repo.create(pl)
    assert created.id is not None
    assert created.title == "My List"

    found = await playlist_repo.get_by_id(created.id)
    assert found is not None
    assert found.title == "My List"


@pytest.mark.asyncio
async def test_list_and_count_playlists(db_session) -> None:
    user_repo = UserRepository(db_session)
    playlist_repo = PlaylistRepository(db_session)

    user = User(full_name="List User", email="list@example.com", password_hash="h")
    created_user = await user_repo.create_user(user)

    for i in range(3):
        await playlist_repo.create(Playlist(user_id=created_user.id, title=f"List {i}"))

    items = await playlist_repo.list_user_playlists(created_user.id, skip=0, limit=2)
    assert len(items) == 2
    assert await playlist_repo.count_user_playlists(created_user.id) == 3


@pytest.mark.asyncio
async def test_soft_delete_playlist(db_session) -> None:
    user_repo = UserRepository(db_session)
    playlist_repo = PlaylistRepository(db_session)

    user = User(full_name="Del User", email="del@example.com", password_hash="h")
    created_user = await user_repo.create_user(user)

    pl = Playlist(user_id=created_user.id, title="To Delete")
    created = await playlist_repo.create(pl)
    await playlist_repo.soft_delete(created)

    assert await playlist_repo.get_by_id(created.id) is None
    assert await playlist_repo.exists(created.id) is False
