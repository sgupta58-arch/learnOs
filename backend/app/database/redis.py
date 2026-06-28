import redis.asyncio as aioredis

from app.core.config import Settings, get_settings

_redis_client: aioredis.Redis | None = None


async def get_redis_client(settings: Settings | None = None) -> aioredis.Redis:
    """Return or create the Redis client connection pool."""
    global _redis_client
    if _redis_client is None:
        settings = settings or get_settings()
        _redis_client = aioredis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def check_redis_connection(settings: Settings | None = None) -> bool:
    """Verify Redis connectivity."""
    client = await get_redis_client(settings)
    return await client.ping()


async def close_redis_client() -> None:
    """Close the Redis client connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
