from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.exceptions.base import AppException
from app.schemas.common import ErrorDetail, error_response

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        errors = [
            ErrorDetail(field=e.get("field"), message=e.get("message", ""))
            for e in exc.errors
        ]
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(message=exc.message, errors=errors),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = [
            ErrorDetail(
                field=".".join(str(loc) for loc in err["loc"]),
                message=err["msg"],
            )
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_response(
                message="Validation error",
                errors=errors,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            "unhandled_exception",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content=error_response(message="Internal server error"),
        )
