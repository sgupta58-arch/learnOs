from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.exceptions.base import ConflictException, NotFoundException
from app.models.user import User
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.services.user import UserService

NOW = datetime.now(UTC)


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> UserService:
    return UserService(mock_repo)


@pytest.mark.asyncio
async def test_create_user_hashes_password(
    service: UserService, mock_repo: AsyncMock
) -> None:
    """Service hashes password and returns response DTO."""
    mock_repo.exists.return_value = False
    created_user = User(
        id=uuid4(),
        full_name="Test User",
        email="test@example.com",
        password_hash="hashed_value",
        is_active=True,
        is_verified=False,
        created_at=NOW,
        updated_at=NOW,
    )
    mock_repo.create_user.return_value = created_user

    data = UserCreateSchema(
        full_name="Test User",
        email="test@example.com",
        password="securepass123",
    )
    result = await service.create_user(data)

    mock_repo.exists.assert_awaited_once_with("test@example.com")
    mock_repo.create_user.assert_awaited_once()
    assert result.email == "test@example.com"
    assert not hasattr(result, "password_hash")


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    service: UserService, mock_repo: AsyncMock
) -> None:
    """Service rejects duplicate email."""
    mock_repo.exists.return_value = True

    data = UserCreateSchema(
        full_name="Test User",
        email="dup@example.com",
        password="securepass123",
    )
    with pytest.raises(ConflictException):
        await service.create_user(data)


@pytest.mark.asyncio
async def test_get_user_not_found(service: UserService, mock_repo: AsyncMock) -> None:
    """Service raises NotFoundException for missing user."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await service.get_user(uuid4())


@pytest.mark.asyncio
async def test_update_user_duplicate_email(
    service: UserService, mock_repo: AsyncMock
) -> None:
    """Service rejects email update when email is taken."""
    user_id = uuid4()
    existing_user = User(
        id=user_id,
        full_name="Owner",
        email="owner@example.com",
        password_hash="hash",
        created_at=NOW,
        updated_at=NOW,
    )
    other_user = User(
        id=uuid4(),
        full_name="Other",
        email="taken@example.com",
        password_hash="hash",
        created_at=NOW,
        updated_at=NOW,
    )
    mock_repo.get_by_id.return_value = existing_user
    mock_repo.get_by_email.return_value = other_user

    data = UserUpdateSchema(email="taken@example.com")
    with pytest.raises(ConflictException):
        await service.update_user(user_id, data)


@pytest.mark.asyncio
async def test_delete_already_deleted_user(
    service: UserService, mock_repo: AsyncMock
) -> None:
    """Service rejects deleting an already soft-deleted user."""
    from datetime import UTC, datetime

    user_id = uuid4()
    deleted_user = User(
        id=user_id,
        full_name="Deleted",
        email="deleted@example.com",
        password_hash="hash",
        deleted_at=datetime.now(UTC),
    )
    mock_repo.get_by_id_including_deleted.return_value = deleted_user

    with pytest.raises(ConflictException, match="already deleted"):
        await service.delete_user(user_id)


@pytest.mark.asyncio
async def test_list_users_returns_dto(
    service: UserService, mock_repo: AsyncMock
) -> None:
    """Service maps entities to list response DTO."""
    user = User(
        id=uuid4(),
        full_name="Listed User",
        email="listed@example.com",
        password_hash="hash",
        is_active=True,
        is_verified=False,
        created_at=NOW,
        updated_at=NOW,
    )
    mock_repo.list_users.return_value = [user]
    mock_repo.count_users.return_value = 1

    result = await service.list_users(skip=0, limit=10)
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].email == "listed@example.com"
