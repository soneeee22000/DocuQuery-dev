"""FastAPI dependencies for authentication."""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.common import AppError
from app.services.user_service import get_user_by_id

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT bearer token, return the current user.

    Raises:
        AppError: 401 if token is invalid, expired, wrong type, or user not found.
    """
    try:
        payload = decode_token(credentials.credentials)
    except JWTError as exc:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid or expired token",
            status_code=401,
        ) from exc

    if payload.get("type") != "access":
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid token type",
            status_code=401,
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid token payload",
            status_code=401,
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise AppError(
            code="INVALID_TOKEN",
            message="Invalid token payload",
            status_code=401,
        ) from exc

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise AppError(
            code="INVALID_TOKEN",
            message="User not found",
            status_code=401,
        )

    return user
