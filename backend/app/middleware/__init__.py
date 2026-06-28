from fastapi import FastAPI

from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware


def register_middleware(app: FastAPI) -> None:
    """Register all custom middleware in the correct order.

    Starlette applies middleware in reverse registration order,
    so the last registered middleware runs first (outermost).
    Desired execution order: CORS -> RequestID -> Timing -> Logging
    """
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
