"""Storage service abstraction and local implementation."""

import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings


class StorageService(ABC):
    """Abstract base class for file storage."""

    @abstractmethod
    async def upload(self, file_data: bytes, filename: str, user_id: uuid.UUID) -> str:
        """Upload a file and return its URL/path."""
        ...

    @abstractmethod
    async def delete(self, file_url: str) -> None:
        """Delete a file by its URL/path."""
        ...


class LocalStorageService(StorageService):
    """Store files on the local filesystem."""

    def __init__(self, base_dir: str = settings.UPLOAD_DIR) -> None:
        self.base_dir = Path(base_dir)

    async def upload(self, file_data: bytes, filename: str, user_id: uuid.UUID) -> str:
        """Save file to uploads/{user_id}/{unique_filename}."""
        user_dir = self.base_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = user_dir / unique_name
        file_path.write_bytes(file_data)

        return str(file_path)

    async def delete(self, file_url: str) -> None:
        """Remove a file from disk. No-op if file doesn't exist."""
        path = Path(file_url)
        if path.exists():
            os.remove(path)
