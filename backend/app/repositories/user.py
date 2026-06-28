from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User persistence operations.

    Only communicates with the database — no business logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def create_user(self, user: User) -> User:
        """Persist a new user entity."""
        return await self.create(user)

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a non-deleted user by email address."""
        stmt = self._not_deleted_filter(select(User).where(User.email == email.lower()))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user(self, user: User, **kwargs) -> User:
        """Update user fields."""
        return await self.update(user, **kwargs)

    async def exists(self, email: str) -> bool:
        """Check whether a non-deleted user with the given email exists."""
        stmt = self._not_deleted_filter(
            select(func.count()).select_from(User).where(User.email == email.lower())
        )
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Return paginated list of non-deleted users."""
        return await self.get_all(skip=skip, limit=limit)

    async def count_users(self) -> int:
        """Count non-deleted users."""
        stmt = self._not_deleted_filter(select(func.count()).select_from(User))
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_by_id_including_deleted(self, user_id: UUID) -> User | None:
        """Retrieve a user by ID including soft-deleted records."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
