"""Document parser tests."""

from pathlib import Path

import pytest

from app.schemas.common import AppError
from app.services.parser import parse_document

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_parse_txt() -> None:
    """Extract text from TXT file."""
    data = (FIXTURES_DIR / "sample.txt").read_bytes()
    text = parse_document(data, "text/plain")
    assert "John Doe" in text
    assert "Python" in text


def test_parse_empty_txt() -> None:
    """Empty TXT raises error."""
    with pytest.raises(AppError, match="no extractable text"):
        parse_document(b"   ", "text/plain")


def test_parse_unsupported_mime() -> None:
    """Unsupported MIME type raises error."""
    with pytest.raises(AppError, match="Cannot parse"):
        parse_document(b"data", "image/png")
