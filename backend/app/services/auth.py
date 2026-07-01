from app.core.security import create_access_token, verify_password
from app.exceptions.base import UnauthorizedException
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequestSchema, TokenResponseSchema


class AuthService:
    """Authentication business logic.

    Handles login credential validation and JWT token issuance.
    Delegates user lookup to UserRepository.
    """

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def login(self, data: LoginRequestSchema) -> TokenResponseSchema:
        """Authenticate a user and return a JWT access token."""
        user = await self.repository.get_by_email(data.email.lower())
        if user is None:
            raise UnauthorizedException(
                message="Invalid email or password",
                errors=[{"field": "email", "message": "Invalid credentials"}],
            )

        if not verify_password(data.password, user.password_hash):
            raise UnauthorizedException(
                message="Invalid email or password",
                errors=[{"field": "password", "message": "Invalid credentials"}],
            )

        access_token = create_access_token(subject=str(user.id))
        return TokenResponseSchema(access_token=access_token)