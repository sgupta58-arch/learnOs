from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateSchema(BaseModel):
    """Schema for creating a new user."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdateSchema(BaseModel):
    """Schema for updating an existing user."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None
    is_verified: bool | None = None
    profile_picture: str | None = Field(default=None, max_length=512)


class UserResponseSchema(BaseModel):
    """Schema for user API responses — never exposes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    profile_picture: str | None
    created_at: datetime
    updated_at: datetime


class UserListResponseSchema(BaseModel):
    """Paginated list of users."""

    items: list[UserResponseSchema]
    total: int
    skip: int
    limit: int
