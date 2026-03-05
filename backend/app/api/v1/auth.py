"""Authentication endpoints."""

import uuid

from fastapi import APIRouter, Depends
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import ApiResponse, AppError
from app.services.user_service import authenticate_user, create_user, get_user_by_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=ApiResponse[TokenResponse],
    status_code=201,
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Register a new user and return tokens."""
    user = await create_user(db, body.email, body.password)
    tokens = TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
    return ApiResponse(data=tokens)


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Authenticate and return tokens."""
    user = await authenticate_user(db, body.email, body.password)
    tokens = TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
    return ApiResponse(data=tokens)


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Exchange a refresh token for a new token pair."""
    try:
        payload = decode_token(body.refresh_token)
    except JWTError as exc:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid or expired refresh token",
            status_code=401,
        ) from exc

    if payload.get("type") != "refresh":
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid token type — expected refresh token",
            status_code=401,
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid token payload",
            status_code=401,
        )

    user_id = uuid.UUID(user_id_str)
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise AppError(
            code="INVALID_TOKEN",
            message="User not found",
            status_code=401,
        )

    tokens = TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
    return ApiResponse(data=tokens)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def me(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserResponse]:
    """Return the current authenticated user."""
    return ApiResponse(data=UserResponse.model_validate(current_user))
