from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import Settings, get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""

    sub: str
    exp: datetime
    type: str = "access"


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    settings = settings or get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
    settings: Settings | None = None,
) -> TokenPayload:
    """Decode and validate a JWT access token."""
    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(
            sub=str(payload["sub"]),
            exp=datetime.fromtimestamp(payload["exp"], tz=UTC),
            type=payload.get("type", "access"),
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
