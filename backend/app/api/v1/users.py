from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.user import get_user_service
from app.schemas.common import success_response
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> dict:
    """List users with pagination."""
    result = await service.list_users(skip=skip, limit=limit)
    return success_response(
        data=result.model_dump(),
        message="Users retrieved successfully",
    )


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> dict:
    """Retrieve a single user by ID."""
    user = await service.get_user(user_id)
    return success_response(
        data=user.model_dump(),
        message="User retrieved successfully",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
) -> dict:
    """Create a new user."""
    user = await service.create_user(data)
    return success_response(
        data=user.model_dump(),
        message="User created successfully",
    )


@router.patch("/{user_id}")
async def update_user(
    user_id: UUID,
    data: UserUpdateSchema,
    service: UserService = Depends(get_user_service),
) -> dict:
    """Update an existing user."""
    user = await service.update_user(user_id, data)
    return success_response(
        data=user.model_dump(),
        message="User updated successfully",
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> dict:
    """Soft delete a user."""
    user = await service.delete_user(user_id)
    return success_response(
        data=user.model_dump(),
        message="User deleted successfully",
    )
