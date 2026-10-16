from typing import Any
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base application exception returning structured errors."""

    def __init__(self, error_code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str):
        super().__init__(
            error_code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationError(AppError):
    """Raised when request payload or parameter validation fails."""

    def __init__(self, message: str):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def format_validation_error_message(errors: list[dict[str, Any]]) -> str:
    """Format Pydantic/FastAPI validation errors into a clean, human-readable message."""
    messages = []
    for err in errors:
        loc = " -> ".join(str(loc_part) for loc_part in err.get("loc", []) if loc_part != "body")
        msg = err.get("msg", "Invalid value")
        # Clean up pydantic prefix "Value error, " if present
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, ") :]
        if loc:
            messages.append(f"{loc}: {msg}")
        else:
            messages.append(msg)
    return "; ".join(messages) if messages else "Invalid request data"


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message},
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI and Pydantic validation errors with HTTP 400."""
    message = format_validation_error_message(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "VALIDATION_ERROR", "message": message},
    )


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions with consistent error response structure."""
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "NOT_FOUND"
    elif exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        code = "METHOD_NOT_ALLOWED"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "VALIDATION_ERROR"
    else:
        code = f"HTTP_{exc.status_code}"

    detail = exc.detail if isinstance(exc.detail, str) else "An error occurred"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": code, "message": detail},
    )


async def global_exception_handler(_: Request, __: Exception) -> JSONResponse:
    """Fallback handler for unhandled exceptions to avoid leaking internals."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred.",
        },
    )

