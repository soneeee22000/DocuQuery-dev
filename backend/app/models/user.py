"""User model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Application user."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)

    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    analyses: Mapped[list["Analysis"]] = relationship(  # noqa: F821
        back_populates="owner",
        cascade="all, delete-orphan",
    )
