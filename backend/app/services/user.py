from uuid import UUID

from app.core.security import hash_password
from app.exceptions.base import ConflictException, NotFoundException
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserCreateSchema,
    UserListResponseSchema,
    UserResponseSchema,
    UserUpdateSchema,
)


class UserService:
    """User business logic layer.

    All user-related rules live here: uniqueness, hashing, validation,
    and DTO mapping. Routes and repositories delegate to this class.
    """

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def _to_response(self, user: User) -> UserResponseSchema:
        """Map a User entity to a response DTO."""
        return UserResponseSchema.model_validate(user)

    async def create_user(self, data: UserCreateSchema) -> UserResponseSchema:
        """Register a new user with a unique email and hashed password."""
        email = data.email.lower()
        if await self.repository.exists(email):
            raise ConflictException(
                message="A user with this email already exists",
                errors=[{"field": "email", "message": "Email already registered"}],
            )

        user = User(
            full_name=data.full_name.strip(),
            email=email,
            password_hash=hash_password(data.password),
            is_active=True,
            is_verified=False,
        )
        created = await self.repository.create_user(user)
        return self._to_response(created)

    async def get_user(self, user_id: UUID) -> UserResponseSchema:
        """Retrieve a single user by ID."""
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(message="User not found")
        return self._to_response(user)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> UserListResponseSchema:
        """Return a paginated list of users."""
        users = await self.repository.list_users(skip=skip, limit=limit)
        total = await self.repository.count_users()
        return UserListResponseSchema(
            items=[self._to_response(u) for u in users],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_user(
        self,
        user_id: UUID,
        data: UserUpdateSchema,
    ) -> UserResponseSchema:
        """Update user profile fields."""
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException(message="User not found")

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] is not None:
            email = update_data["email"].lower()
            existing = await self.repository.get_by_email(email)
            if existing is not None and existing.id != user.id:
                raise ConflictException(
                    message="A user with this email already exists",
                    errors=[{"field": "email", "message": "Email already registered"}],
                )
            update_data["email"] = email

        if "password" in update_data and update_data["password"] is not None:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        if "full_name" in update_data and update_data["full_name"] is not None:
            update_data["full_name"] = update_data["full_name"].strip()

        updated = await self.repository.update_user(user, **update_data)
        return self._to_response(updated)

    async def delete_user(self, user_id: UUID) -> UserResponseSchema:
        """Soft delete a user."""
        user = await self.repository.get_by_id_including_deleted(user_id)
        if user is None:
            raise NotFoundException(message="User not found")
        if user.is_deleted:
            raise ConflictException(message="User is already deleted")

        deleted = await self.repository.soft_delete(user)
        return self._to_response(deleted)
