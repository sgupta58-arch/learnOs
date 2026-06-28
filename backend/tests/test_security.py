from datetime import UTC, datetime, timedelta

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password() -> None:
    """Password hashing and verification work correctly."""
    plain = "securepassword123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_access_token(test_settings) -> None:
    """JWT tokens can be created and decoded."""
    token = create_access_token(
        subject="user-123",
        settings=test_settings,
        expires_delta=timedelta(minutes=30),
    )
    payload = decode_access_token(token, settings=test_settings)
    assert payload.sub == "user-123"
    assert payload.type == "access"
    assert payload.exp > datetime.now(UTC)


def test_decode_invalid_token_raises(test_settings) -> None:
    """Invalid tokens raise ValueError."""
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token("invalid.token.here", settings=test_settings)
