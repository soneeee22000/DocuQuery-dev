"""Document upload and management endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.document import Document
from app.models.user import User
from app.schemas.common import ApiResponse, AppError
from app.schemas.document import DocType, DocumentResponse
from app.services.parser import parse_document
from app.services.storage import LocalStorageService, StorageService
from app.utils.file_validation import validate_file

router = APIRouter(prefix="/documents", tags=["documents"])


def get_storage() -> StorageService:
    """Return the storage service instance."""
    return LocalStorageService()


@router.post("/upload", response_model=ApiResponse[DocumentResponse], status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: DocType = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage),
) -> ApiResponse[DocumentResponse]:
    """Upload a document, extract text, and store metadata."""
    file_data = await file.read()
    filename = file.filename or "unnamed"

    mime_type = validate_file(file_data, filename)
    extracted_text = parse_document(file_data, mime_type)
    file_url = await storage.upload(file_data, filename, current_user.id)

    document = Document(
        user_id=current_user.id,
        name=filename,
        doc_type=doc_type.value,
        mime_type=mime_type,
        file_url=file_url,
        file_size=len(file_data),
        extracted_text=extracted_text,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    return ApiResponse(data=DocumentResponse.model_validate(document))


@router.get("/", response_model=ApiResponse[list[DocumentResponse]])
async def list_documents(
    doc_type: DocType | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[list[DocumentResponse]]:
    """List the current user's documents, optionally filtered by type."""
    stmt = select(Document).where(Document.user_id == current_user.id)
    if doc_type is not None:
        stmt = stmt.where(Document.doc_type == doc_type.value)
    stmt = stmt.order_by(Document.created_at.desc())

    result = await db.execute(stmt)
    documents = result.scalars().all()

    return ApiResponse(data=[DocumentResponse.model_validate(d) for d in documents])


@router.delete("/{document_id}", response_model=ApiResponse[None])
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage),
) -> ApiResponse[None]:
    """Delete a document (owner only)."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if document is None:
        raise AppError(
            code="NOT_FOUND",
            message="Document not found",
            status_code=404,
        )

    if document.user_id != current_user.id:
        raise AppError(
            code="FORBIDDEN",
            message="You do not own this document",
            status_code=403,
        )

    await storage.delete(document.file_url)
    await db.delete(document)

    return ApiResponse(data=None)
