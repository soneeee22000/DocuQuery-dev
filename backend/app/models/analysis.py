"""Analysis model."""

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Analysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Match analysis between a resume and job description."""

    __tablename__ = "analyses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    jd_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    results: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    tips: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    llm_model: Mapped[str] = mapped_column(
        String(100), nullable=False, default="gpt-4o-mini"
    )

    owner: Mapped["User"] = relationship(  # noqa: F821
        back_populates="analyses",
    )
    resume: Mapped["Document"] = relationship(  # noqa: F821
        foreign_keys=[resume_id],
        lazy="joined",
    )
    jd: Mapped["Document"] = relationship(  # noqa: F821
        foreign_keys=[jd_id],
        lazy="joined",
    )
