from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import TokenPayload, decode_access_token
from app.exceptions.base import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> TokenPayload:
    """Decode and validate the JWT token from the Authorization header."""
    if token is None:
        raise UnauthorizedException(message="Not authenticated")

    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedException(message="Invalid or expired token") from exc


async def get_current_user(
    token_payload: Annotated[TokenPayload, Depends(get_current_user_token)],
) -> Any:
    """Return the current authenticated user.

    Auth endpoints and User model are not yet implemented.
    This dependency validates the token but raises 501 until Phase 2.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication endpoints not yet implemented",
    )


async def get_current_active_user(
    current_user: Annotated[Any, Depends(get_current_user)],
) -> Any:
    """Return the current active user. Reserved for Phase 2."""
    return current_user
