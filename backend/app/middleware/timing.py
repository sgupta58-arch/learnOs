import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """Record request start time for duration calculation."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request.state.start_time = time.perf_counter()
        return await call_next(request)
