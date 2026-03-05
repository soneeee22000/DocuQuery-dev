"""File validation tests."""

import pytest

from app.schemas.common import AppError
from app.utils.file_validation import validate_file


def test_validate_valid_pdf() -> None:
    """Valid PDF passes validation."""
    data = b"%PDF-1.4 fake pdf content"
    mime = validate_file(data, "resume.pdf")
    assert mime == "application/pdf"


def test_validate_valid_docx() -> None:
    """Valid DOCX (PK header) passes validation."""
    data = b"PK\x03\x04 fake docx content"
    mime = validate_file(data, "resume.docx")
    assert "wordprocessingml" in mime


def test_validate_valid_txt() -> None:
    """Valid TXT passes validation (no magic bytes check)."""
    data = b"Just some text content"
    mime = validate_file(data, "notes.txt")
    assert mime == "text/plain"


def test_validate_too_large() -> None:
    """File exceeding size limit raises error."""
    data = b"x" * (11 * 1024 * 1024)
    with pytest.raises(AppError, match="exceeds"):
        validate_file(data, "big.pdf")


def test_validate_unsupported_extension() -> None:
    """Unsupported extension raises error."""
    with pytest.raises(AppError, match="Unsupported"):
        validate_file(b"data", "file.exe")


def test_validate_magic_bytes_mismatch() -> None:
    """PDF extension with wrong magic bytes raises error."""
    data = b"NOT A PDF FILE"
    with pytest.raises(AppError, match="does not match"):
        validate_file(data, "fake.pdf")
