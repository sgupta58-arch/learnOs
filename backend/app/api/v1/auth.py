from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.auth import get_auth_service
from app.schemas.auth import LoginRequestSchema, TokenResponseSchema
from app.schemas.common import success_response
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """Authenticate a user and return a JWT access token."""

    data = LoginRequestSchema(
        email=form_data.username,
        password=form_data.password,
    )

    token = await service.login(data)

    return success_response(
        data=token.model_dump(),
        message="Login successful",
    )
    
    
    
@router.post(
    "/token",
    response_model=TokenResponseSchema,
    
)
async def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    data = LoginRequestSchema(
        email=form_data.username,
        password=form_data.password,
    )

    token = await service.login(data)

    return token