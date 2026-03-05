"""Document text extraction."""

import io

import fitz
from docx import Document

from app.schemas.common import AppError

MIME_PDF = "application/pdf"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_TXT = "text/plain"


def parse_document(file_data: bytes, mime_type: str) -> str:
    """Extract text from a document file.

    Args:
        file_data: Raw bytes of the uploaded file.
        mime_type: MIME type of the file.

    Returns:
        Extracted text content.

    Raises:
        AppError: If extraction fails or content is empty.
    """
    if mime_type == MIME_PDF:
        text = _extract_pdf(file_data)
    elif mime_type == MIME_DOCX:
        text = _extract_docx(file_data)
    elif mime_type == MIME_TXT:
        text = _extract_txt(file_data)
    else:
        raise AppError(
            code="UNSUPPORTED_FORMAT",
            message=f"Cannot parse MIME type: {mime_type}",
            status_code=400,
        )

    if not text.strip():
        raise AppError(
            code="EMPTY_DOCUMENT",
            message="Document contains no extractable text",
            status_code=400,
        )

    return text.strip()


def _extract_pdf(file_data: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(stream=file_data, filetype="pdf")
        pages: list[str] = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        return "\n".join(pages)
    except Exception as exc:
        raise AppError(
            code="PARSE_ERROR",
            message=f"Failed to parse PDF: {exc}",
            status_code=400,
        ) from exc


def _extract_docx(file_data: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        doc = Document(io.BytesIO(file_data))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception as exc:
        raise AppError(
            code="PARSE_ERROR",
            message=f"Failed to parse DOCX: {exc}",
            status_code=400,
        ) from exc


def _extract_txt(file_data: bytes) -> str:
    """Extract text from TXT file."""
    try:
        return file_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return file_data.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise AppError(
                code="PARSE_ERROR",
                message="Failed to decode text file",
                status_code=400,
            ) from exc
