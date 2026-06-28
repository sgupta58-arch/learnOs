from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

ModelT = TypeVar("ModelT")


class ErrorDetail(BaseModel):
    """Single validation or application error detail."""

    field: str | None = None
    message: str


class ApiResponse(BaseModel, Generic[ModelT]):
    """Standard API response envelope."""

    model_config = ConfigDict(from_attributes=True)

    success: bool
    message: str
    errors: list[ErrorDetail] = []
    data: ModelT | None = None


def success_response(
    data: Any = None,
    message: str = "Success",
) -> dict[str, Any]:
    """Build a successful API response envelope."""
    return {
        "success": True,
        "message": message,
        "errors": [],
        "data": data,
    }


def error_response(
    message: str,
    errors: list[ErrorDetail] | None = None,
    data: Any = None,
) -> dict[str, Any]:
    """Build an error API response envelope."""
    return {
        "success": False,
        "message": message,
        "errors": [e.model_dump() for e in (errors or [])],
        "data": data,
    }
