"""Storage service tests."""

import uuid
from pathlib import Path

import pytest

from app.services.storage import LocalStorageService


@pytest.fixture
def storage(tmp_path: Path) -> LocalStorageService:
    """Create a LocalStorageService with a temp directory."""
    return LocalStorageService(base_dir=str(tmp_path))


async def test_upload_creates_file(storage: LocalStorageService) -> None:
    """Upload creates a file and returns its path."""
    user_id = uuid.uuid4()
    path = await storage.upload(b"file content", "test.txt", user_id)
    assert Path(path).exists()
    assert Path(path).read_bytes() == b"file content"


async def test_delete_removes_file(storage: LocalStorageService) -> None:
    """Delete removes the uploaded file."""
    user_id = uuid.uuid4()
    path = await storage.upload(b"content", "test.txt", user_id)
    assert Path(path).exists()
    await storage.delete(path)
    assert not Path(path).exists()


async def test_delete_nonexistent_no_error(storage: LocalStorageService) -> None:
    """Delete of nonexistent file does not raise."""
    await storage.delete("/nonexistent/path/file.txt")
