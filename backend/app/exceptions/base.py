class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: list[dict[str, str | None]] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        errors: list[dict[str, str | None]] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=404, errors=errors)


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(
        self,
        message: str = "Unauthorized",
        errors: list[dict[str, str | None]] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, errors=errors)


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(
        self,
        message: str = "Forbidden",
        errors: list[dict[str, str | None]] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=403, errors=errors)


class ConflictException(AppException):
    """Resource conflict exception."""

    def __init__(
        self,
        message: str = "Conflict",
        errors: list[dict[str, str | None]] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=409, errors=errors)
