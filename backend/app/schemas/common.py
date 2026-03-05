"""Common response schemas."""

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error detail in API responses."""

    code: str
    message: str


class ApiResponse[T](BaseModel):
    """Standard API response wrapper."""

    data: T | None = None
    error: ErrorDetail | None = None
    meta: dict[str, Any] = {}


class AppError(Exception):
    """Application error that maps to an API error response."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)
