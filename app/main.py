from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import (
    AppError,
    app_error_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.models import HealthResponse
from app.routes import router as employee_router


def create_app() -> FastAPI:
    """FastAPI application factory with exception handlers and routes configured."""
    application = FastAPI(
        title="JTRONIX Employee REST API",
        version="1.0.0",
        description=(
            "Production-grade in-memory REST API for employee management built for "
            "the JTRONIX backend assessment. Supports listing, filtering by department, "
            "retrieval by ID, creation, and status transitions."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register custom exception handlers for consistent error responses
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(Exception, global_exception_handler)

    # Health check endpoint
    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Service health check",
        description="Returns the operational status of the service.",
    )
    def health_check() -> HealthResponse:
        return HealthResponse(status="ok")

    # Include API Routers
    application.include_router(employee_router)

    return application


app = create_app()
