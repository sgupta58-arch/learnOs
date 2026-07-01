from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.playlists import router as playlists_router
from app.api.v1.videos import router as videos_router
from app.api.v1.progress import router as progress_router
from app.database.redis import check_redis_connection
from app.database.session import check_database_connection, get_db
from app.schemas.common import success_response

router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(playlists_router)
router.include_router(videos_router)
router.include_router(progress_router)


@router.get("/health")
async def liveness_check() -> dict:
    """Liveness probe — confirms the application process is running."""
    return success_response(data={"status": "alive"}, message="Service is alive")


@router.get("/health/ready")
async def readiness_check(
    _db: AsyncSession = Depends(get_db),
) -> dict:
    """Readiness probe — confirms database and Redis connectivity."""
    db_ok = await check_database_connection()
    redis_ok = await check_redis_connection()
    status_value = "ready" if db_ok and redis_ok else "degraded"
    return success_response(
        data={
            "status": status_value,
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
        },
        message="Readiness check complete",
    )
