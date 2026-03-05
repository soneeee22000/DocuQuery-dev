"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])


class HealthData(ApiResponse[dict[str, str]]):
    """Health check response."""

    pass


@router.get("/health", response_model=ApiResponse[dict[str, str]])
async def health_check() -> ApiResponse[dict[str, str]]:
    """Return application health status."""
    return ApiResponse(
        data={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )
