import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request details including method, route, status, and duration."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)

        start_time = getattr(request.state, "start_time", None)
        duration_ms = None
        if start_time is not None:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "request_completed",
            request_id=getattr(request.state, "request_id", None),
            method=request.method,
            route=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response
