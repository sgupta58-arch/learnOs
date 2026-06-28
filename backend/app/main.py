from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.config import Settings, get_settings
from app.core.logging import get_logger, setup_logging
from app.database.redis import close_redis_client
from app.database.session import dispose_engine
from app.exceptions.handlers import register_exception_handlers
from app.middleware import register_middleware
from app.middleware.cors import setup_cors

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    settings: Settings = app.state.settings
    setup_logging(settings)
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )
    yield
    await close_redis_client()
    await dispose_engine()
    logger.info("application_shutdown")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory — creates and configures the FastAPI instance."""
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )
    app.state.settings = settings

    setup_cors(app, settings)
    register_middleware(app)
    register_exception_handlers(app)

    app.include_router(v1_router, prefix="/api/v1", tags=["v1"])

    @app.get("/health", tags=["health"])
    async def root_health() -> dict:
        from app.schemas.common import success_response

        return success_response(data={"status": "alive"}, message="Service is alive")

    return app


app = create_app()


def run() -> None:
    """Entry point for poetry script."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
    )
