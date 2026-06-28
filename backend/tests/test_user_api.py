from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.dependencies.user import get_user_service
from app.schemas.user import UserListResponseSchema, UserResponseSchema

NOW = datetime.now(UTC)


@pytest.fixture
async def user_client(app, mock_user_service: AsyncMock):
    """Client with mocked UserService."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_user_service
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user_api(user_client) -> None:
    """POST /users creates a user and returns envelope."""
    client, mock_service = user_client
    user_id = uuid4()
    mock_service.create_user.return_value = UserResponseSchema(
        id=user_id,
        full_name="API User",
        email="api@example.com",
        is_active=True,
        is_verified=False,
        profile_picture=None,
        created_at=NOW,
        updated_at=NOW,
    )

    response = await client.post(
        "/api/v1/users",
        json={
            "full_name": "API User",
            "email": "api@example.com",
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "api@example.com"


@pytest.mark.asyncio
async def test_get_user_api(user_client) -> None:
    """GET /users/{id} returns a user."""
    client, mock_service = user_client
    user_id = uuid4()
    mock_service.get_user.return_value = UserResponseSchema(
        id=user_id,
        full_name="Get User",
        email="get@example.com",
        is_active=True,
        is_verified=False,
        profile_picture=None,
        created_at=NOW,
        updated_at=NOW,
    )

    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == "Get User"


@pytest.mark.asyncio
async def test_list_users_api(user_client) -> None:
    """GET /users returns paginated list."""
    client, mock_service = user_client

    mock_service.list_users.return_value = UserListResponseSchema(
        items=[],
        total=0,
        skip=0,
        limit=100,
    )

    response = await client.get("/api/v1/users")
    assert response.status_code == 200
    assert response.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_create_user_validation_error(user_client) -> None:
    """POST /users rejects invalid payload."""
    client, _ = user_client
    response = await client.post(
        "/api/v1/users",
        json={"full_name": "", "email": "bad-email", "password": "short"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_user_integration(integration_client: AsyncClient) -> None:
    """End-to-end user creation against test database."""
    response = await integration_client.post(
        "/api/v1/users",
        json={
            "full_name": "Integration User",
            "email": "integration@example.com",
            "password": "securepass123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "integration@example.com"

    user_id = body["data"]["id"]
    get_response = await integration_client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["full_name"] == "Integration User"
