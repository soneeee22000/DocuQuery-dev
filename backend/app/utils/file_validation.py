"""File validation utilities."""

from app.core.config import settings
from app.schemas.common import AppError

ALLOWED_MIME_TYPES: dict[str, list[bytes]] = {
    "application/pdf": [b"%PDF"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        b"PK\x03\x04",
        b"PK\x05\x06",
    ],
    "text/plain": [],
}

EXTENSION_TO_MIME: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
}

MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def get_mime_from_extension(filename: str) -> str:
    """Determine MIME type from file extension.

    Raises:
        AppError: If extension is not supported.
    """
    ext = "." + filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    mime = EXTENSION_TO_MIME.get(ext)
    if mime is None:
        raise AppError(
            code="UNSUPPORTED_FORMAT",
            message=f"Unsupported file format: {ext or 'unknown'}",
            status_code=400,
        )
    return mime


def validate_file(
    file_data: bytes,
    filename: str,
) -> str:
    """Validate file size, extension, and magic bytes.

    Returns:
        The detected MIME type.

    Raises:
        AppError: If validation fails.
    """
    if len(file_data) > MAX_UPLOAD_BYTES:
        raise AppError(
            code="FILE_TOO_LARGE",
            message=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
            status_code=400,
        )

    mime = get_mime_from_extension(filename)
    magic_signatures = ALLOWED_MIME_TYPES[mime]

    if magic_signatures and not any(
        file_data.startswith(sig) for sig in magic_signatures
    ):
        raise AppError(
            code="INVALID_FILE",
            message="File content does not match its extension",
            status_code=400,
        )

    return mime
