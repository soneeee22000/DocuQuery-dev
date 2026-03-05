"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.health import router as health_router
from app.core.config import settings
from app.schemas.common import ApiResponse, AppError, ErrorDetail

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors with consistent response shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse[None](
            error=ErrorDetail(code=exc.code, message=exc.message)
        ).model_dump(),
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation errors with consistent response shape."""
    return JSONResponse(
        status_code=422,
        content=ApiResponse[None](
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(exc),
            )
        ).model_dump(),
    )


# Register routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
