"""User service for registration, authentication, and lookup."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.common import AppError


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Look up a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Look up a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    """Create a new user.

    Raises:
        AppError: 409 if email already exists.
    """
    existing = await get_user_by_email(db, email)
    if existing is not None:
        raise AppError(
            code="DUPLICATE_EMAIL",
            message="A user with this email already exists",
            status_code=409,
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Authenticate a user by email and password.

    Raises:
        AppError: 401 if credentials are invalid.
    """
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise AppError(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password",
            status_code=401,
        )
    return user
