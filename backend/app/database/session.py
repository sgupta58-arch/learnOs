from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings

_engine = None
_session_factory = None


def get_engine(settings: Settings | None = None):
    """Return or create the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = settings or get_settings()
        _engine = create_async_engine(
            settings.effective_database_url,
            pool_pre_ping=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            echo=settings.DEBUG,
        )
    return _engine


def get_session_factory(
    settings: Settings | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Return or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine(settings)
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a database session per request."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection(settings: Settings | None = None) -> bool:
    """Verify database connectivity."""
    from sqlalchemy import text

    settings = settings or get_settings()
    engine = get_engine(settings)
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True


async def dispose_engine() -> None:
    """Dispose of the database engine and reset globals."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
