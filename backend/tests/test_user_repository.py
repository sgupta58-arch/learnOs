import pytest

from app.models.user import User
from app.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_create_user(db_session) -> None:
    """Repository persists a new user entity."""
    repo = UserRepository(db_session)
    user = User(
        full_name="Jane Doe",
        email="jane@example.com",
        password_hash="hashed",
    )
    created = await repo.create_user(user)
    assert created.id is not None
    assert created.email == "jane@example.com"


@pytest.mark.asyncio
async def test_get_by_id(db_session) -> None:
    """Repository retrieves user by ID."""
    repo = UserRepository(db_session)
    user = User(
        full_name="John Doe",
        email="john@example.com",
        password_hash="hashed",
    )
    created = await repo.create_user(user)
    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.full_name == "John Doe"


@pytest.mark.asyncio
async def test_get_by_email(db_session) -> None:
    """Repository retrieves user by email."""
    repo = UserRepository(db_session)
    user = User(
        full_name="Email User",
        email="emailuser@example.com",
        password_hash="hashed",
    )
    await repo.create_user(user)
    found = await repo.get_by_email("emailuser@example.com")
    assert found is not None
    assert found.full_name == "Email User"


@pytest.mark.asyncio
async def test_exists(db_session) -> None:
    """Repository checks email existence."""
    repo = UserRepository(db_session)
    assert await repo.exists("new@example.com") is False

    user = User(
        full_name="Exists User",
        email="exists@example.com",
        password_hash="hashed",
    )
    await repo.create_user(user)
    assert await repo.exists("exists@example.com") is True


@pytest.mark.asyncio
async def test_list_users(db_session) -> None:
    """Repository returns paginated user list."""
    repo = UserRepository(db_session)
    for i in range(3):
        await repo.create_user(
            User(
                full_name=f"User {i}",
                email=f"user{i}@example.com",
                password_hash="hashed",
            )
        )
    users = await repo.list_users(skip=0, limit=2)
    assert len(users) == 2
    assert await repo.count_users() == 3


@pytest.mark.asyncio
async def test_update_user(db_session) -> None:
    """Repository updates user fields."""
    repo = UserRepository(db_session)
    user = User(
        full_name="Before Update",
        email="update@example.com",
        password_hash="hashed",
    )
    created = await repo.create_user(user)
    updated = await repo.update_user(created, full_name="After Update")
    assert updated.full_name == "After Update"


@pytest.mark.asyncio
async def test_soft_delete_excludes_from_queries(db_session) -> None:
    """Soft-deleted users are excluded from standard queries."""
    repo = UserRepository(db_session)
    user = User(
        full_name="Delete Me",
        email="delete@example.com",
        password_hash="hashed",
    )
    created = await repo.create_user(user)
    await repo.soft_delete(created)

    assert await repo.get_by_id(created.id) is None
    assert await repo.get_by_email("delete@example.com") is None
    assert await repo.exists("delete@example.com") is False

    found = await repo.get_by_id_including_deleted(created.id)
    assert found is not None
    assert found.is_deleted is True
