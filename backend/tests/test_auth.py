"""Authentication tests covering schemas, service, API, and dependency."""
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token, hash_password
from app.dependencies.auth import get_auth_service, get_current_user
from app.exceptions.base import UnauthorizedException
from app.models.user import User
from app.schemas.auth import LoginRequestSchema, TokenResponseSchema
from app.services.auth import AuthService

NOW = datetime.now(UTC)


# ---------------------------------------------------------------------------
# Milestone 1 – Schema validation
# ---------------------------------------------------------------------------


def test_login_request_schema_valid() -> None:
    """LoginRequestSchema accepts valid email and password."""
    schema = LoginRequestSchema(email="user@example.com", password="securepass")
    assert schema.email == "user@example.com"
    assert schema.password == "securepass"


def test_login_request_schema_rejects_empty_password() -> None:
    """LoginRequestSchema rejects an empty password."""
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        LoginRequestSchema(email="user@example.com", password="")


def test_login_request_schema_rejects_invalid_email() -> None:
    """LoginRequestSchema rejects a malformed email."""
    import pydantic

    with pytest.raises(pydantic.ValidationError):
        LoginRequestSchema(email="not-an-email", password="securepass")


def test_token_response_schema_defaults() -> None:
    """TokenResponseSchema sets token_type to 'bearer' by default."""
    schema = TokenResponseSchema(access_token="abc.def.ghi")
    assert schema.token_type == "bearer"
    assert schema.access_token == "abc.def.ghi"


# ---------------------------------------------------------------------------
# Milestone 2 – AuthService unit tests
# ---------------------------------------------------------------------------


def _make_user(
    *,
    email: str = "user@example.com",
    password: str = "securepass123",
    is_active: bool = True,
) -> User:
    """Build a User model instance with a hashed password."""
    user = User(
        full_name="Test User",
        email=email,
        password_hash=hash_password(password),
        is_active=is_active,
        is_verified=True,
    )
    user.id = uuid4()
    user.created_at = NOW
    user.updated_at = NOW
    user.deleted_at = None
    return user


@pytest.mark.asyncio
async def test_auth_service_login_success(test_settings) -> None:
    """AuthService.login returns a token for valid credentials."""
    user = _make_user()
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = user

    service = AuthService(mock_repo)
    with patch("app.services.auth.create_access_token") as mock_create:
        mock_create.return_value = "mocked.jwt.token"
        result = await service.login(
            LoginRequestSchema(email="user@example.com", password="securepass123")
        )

    assert isinstance(result, TokenResponseSchema)
    assert result.access_token == "mocked.jwt.token"
    assert result.token_type == "bearer"
    mock_repo.get_by_email.assert_awaited_once_with("user@example.com")


@pytest.mark.asyncio
async def test_auth_service_login_user_not_found() -> None:
    """AuthService.login raises UnauthorizedException when user doesn't exist."""
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None

    service = AuthService(mock_repo)
    with pytest.raises(UnauthorizedException, match="Invalid email or password"):
        await service.login(
            LoginRequestSchema(email="ghost@example.com", password="anypassword")
        )


@pytest.mark.asyncio
async def test_auth_service_login_wrong_password() -> None:
    """AuthService.login raises UnauthorizedException for wrong password."""
    user = _make_user(password="correctpassword")
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = user

    service = AuthService(mock_repo)
    with pytest.raises(UnauthorizedException, match="Invalid email or password"):
        await service.login(
            LoginRequestSchema(email="user@example.com", password="wrongpassword")
        )


@pytest.mark.asyncio
async def test_auth_service_login_normalises_email() -> None:
    """AuthService.login lowercases the email before lookup."""
    user = _make_user(email="user@example.com")
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = user

    service = AuthService(mock_repo)
    with patch("app.services.auth.create_access_token", return_value="tok"):
        await service.login(
            LoginRequestSchema(email="USER@EXAMPLE.COM", password="securepass123")
        )

    mock_repo.get_by_email.assert_awaited_once_with("user@example.com")


# ---------------------------------------------------------------------------
# Milestone 3 – Auth API endpoint tests
# ---------------------------------------------------------------------------


@pytest.fixture
async def auth_client(app):
    """Client with mocked AuthService."""
    mock_service = AsyncMock(spec=AuthService)
    app.dependency_overrides[get_auth_service] = lambda: mock_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_service

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_endpoint_success(auth_client) -> None:
    """POST /api/v1/auth/login returns 200 with access_token on valid credentials."""
    client, mock_service = auth_client
    mock_service.login.return_value = TokenResponseSchema(
        access_token="valid.jwt.token"
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "securepass123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "valid.jwt.token"
    assert body["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_endpoint_invalid_credentials(auth_client) -> None:
    """POST /api/v1/auth/login returns 401 for invalid credentials."""
    client, mock_service = auth_client
    mock_service.login.side_effect = UnauthorizedException(
        message="Invalid email or password"
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_login_endpoint_missing_fields(auth_client) -> None:
    """POST /api/v1/auth/login returns 422 when required fields are missing."""
    client, _ = auth_client
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com"},  # missing password
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_endpoint_invalid_email_format(auth_client) -> None:
    """POST /api/v1/auth/login returns 422 for malformed email."""
    client, _ = auth_client
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "securepass123"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Milestone 4 – get_current_user dependency tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_current_user_returns_user(test_settings) -> None:
    """get_current_user resolves a valid token to a User model."""
    user = _make_user()
    token = create_access_token(subject=str(user.id), settings=test_settings)

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = user

    from app.core.security import decode_access_token
    from app.dependencies.auth import get_current_user_token

    token_payload = decode_access_token(token, settings=test_settings)

    with patch("app.dependencies.auth.UserRepository", return_value=mock_repo):
        db_mock = AsyncMock()
        result = await get_current_user(token_payload=token_payload, db=db_mock)

    assert result is user
    mock_repo.get_by_id.assert_awaited_once_with(user.id)


@pytest.mark.asyncio
async def test_get_current_user_raises_when_user_not_found(test_settings) -> None:
    """get_current_user raises UnauthorizedException when user is missing from DB."""
    user_id = uuid4()
    token = create_access_token(subject=str(user_id), settings=test_settings)

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None

    from app.core.security import decode_access_token

    token_payload = decode_access_token(token, settings=test_settings)

    with patch("app.dependencies.auth.UserRepository", return_value=mock_repo):
        db_mock = AsyncMock()
        with pytest.raises(UnauthorizedException, match="User not found"):
            await get_current_user(token_payload=token_payload, db=db_mock)


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    """Endpoints requiring auth return 401 when no token is provided."""
    # The /users/{id}/playlists endpoint uses get_current_user_token
    response = await client.get(f"/api/v1/users/{uuid4()}/playlists")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient) -> None:
    """Endpoints requiring auth return 401 for an invalid token."""
    response = await client.get(
        f"/api/v1/users/{uuid4()}/playlists",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_integration(integration_client: AsyncClient) -> None:
    """End-to-end: register a user then log in and receive a JWT."""
    # Register
    register_resp = await integration_client.post(
        "/api/v1/users",
        json={
            "full_name": "Auth Integration User",
            "email": "authintegration@example.com",
            "password": "securepass123",
        },
    )
    assert register_resp.status_code == 201

    # Login
    login_resp = await integration_client.post(
        "/api/v1/auth/login",
        json={"email": "authintegration@example.com", "password": "securepass123"},
    )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_integration_wrong_password(integration_client: AsyncClient) -> None:
    """End-to-end: login with wrong password returns 401."""
    # Register
    await integration_client.post(
        "/api/v1/users",
        json={
            "full_name": "Wrong Pass User",
            "email": "wrongpass@example.com",
            "password": "correctpassword123",
        },
    )

    # Login with wrong password
    login_resp = await integration_client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"},
    )
    assert login_resp.status_code == 401
