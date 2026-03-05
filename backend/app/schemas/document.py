"""Document schemas."""

import enum
import uuid
from datetime import datetime

from pydantic import BaseModel


class DocType(enum.StrEnum):
    """Document type enum."""

    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"


class DocumentResponse(BaseModel):
    """Document response schema."""

    id: uuid.UUID
    name: str
    doc_type: DocType
    mime_type: str
    file_size: int
    extracted_text: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
