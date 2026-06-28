from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """Generic repository providing CRUD operations with soft-delete support."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def _not_deleted_filter(self, stmt):
        """Apply soft-delete filter to a query statement."""
        return stmt.where(self.model.deleted_at.is_(None))

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        """Retrieve a single entity by ID, excluding soft-deleted records."""
        stmt = self._not_deleted_filter(
            select(self.model).where(self.model.id == entity_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        """Retrieve all non-deleted entities with pagination."""
        stmt = self._not_deleted_filter(select(self.model).offset(skip).limit(limit))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entity: ModelT) -> ModelT:
        """Persist a new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT, **kwargs) -> ModelT:
        """Update entity fields."""
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def soft_delete(self, entity: ModelT) -> ModelT:
        """Soft delete an entity by setting deleted_at timestamp."""
        entity.deleted_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def hard_delete(self, entity: ModelT) -> None:
        """Permanently delete an entity from the database."""
        await self.session.delete(entity)
        await self.session.flush()
