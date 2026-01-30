
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO, Optional


@dataclass
class StoredFile:
    """Represents a stored file."""

    key: str  # Unique identifier/path
    url: str  # Public or signed URL
    size_bytes: int
    content_type: str


class StoragePort(ABC):
    """
    Abstract interface for file storage operations.
    """

    @abstractmethod
    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[dict[str, str]] = None,
    ) -> StoredFile:
        """
        Upload a file to storage.

        Args:
            file: File-like object to upload.
            key: Storage key/path for the file.
            content_type: MIME type of the file.
            metadata: Optional metadata to store with the file.

        Returns:
            StoredFile with URL and metadata.
        """
        ...

    @abstractmethod
    def download(self, key: str) -> BinaryIO:
        """
        Download a file from storage.

        Args:
            key: Storage key/path of the file.

        Returns:
            File-like object with the file contents.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a file from storage.

        Args:
            key: Storage key/path of the file.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for temporary access.

        Args:
            key: Storage key/path of the file.
            expires_in: URL expiration in seconds.

        Returns:
            Signed URL string.
        """
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            key: Storage key/path to check.

        Returns:
            True if exists, False otherwise.
        """
        ...
