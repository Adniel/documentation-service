"""Storage backend abstraction for attachments.

Sprint F: Attachments & Media Support

Provides pluggable storage backends for binary file storage.
- LocalFilesystemStorage: Development and single-server deployments
- S3Storage: Production deployments with S3-compatible object storage
"""

import os
import shutil
from abc import ABC, abstractmethod
from io import BytesIO
from typing import BinaryIO

import aiofiles
import aiofiles.os


class StorageBackend(ABC):
    """Abstract base class for attachment storage backends."""

    @abstractmethod
    async def put(self, key: str, data: BinaryIO, content_type: str) -> str:
        """Store a file and return the storage key.

        Args:
            key: Storage key path (e.g., org_id/page_id/attachment_id/v1/file.pdf)
            data: File data as binary stream
            content_type: MIME type of the file

        Returns:
            The storage key used to retrieve the file
        """
        ...

    @abstractmethod
    async def get(self, key: str) -> BinaryIO:
        """Retrieve a file by storage key.

        Args:
            key: Storage key path

        Returns:
            File data as binary stream

        Raises:
            FileNotFoundError: If the file does not exist
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a file by storage key.

        Args:
            key: Storage key path

        Returns:
            True if deleted, False if not found
        """
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a file exists at the given key.

        Args:
            key: Storage key path

        Returns:
            True if file exists
        """
        ...


class LocalFilesystemStorage(StorageBackend):
    """Store files on the local filesystem.

    Suitable for development and single-server deployments.
    Files are stored under a configurable base directory.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path

    def _full_path(self, key: str) -> str:
        """Get full filesystem path for a storage key."""
        # Prevent path traversal
        safe_key = os.path.normpath(key).lstrip(os.sep)
        return os.path.join(self.base_path, safe_key)

    async def put(self, key: str, data: BinaryIO, content_type: str) -> str:
        full_path = self._full_path(key)
        dir_path = os.path.dirname(full_path)

        await aiofiles.os.makedirs(dir_path, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            # Read in chunks to handle large files
            while True:
                chunk = data.read(8192)
                if not chunk:
                    break
                await f.write(chunk)

        return key

    async def get(self, key: str) -> BinaryIO:
        full_path = self._full_path(key)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {key}")

        # Read into memory for streaming
        async with aiofiles.open(full_path, "rb") as f:
            content = await f.read()

        return BytesIO(content)

    async def delete(self, key: str) -> bool:
        full_path = self._full_path(key)

        if not os.path.exists(full_path):
            return False

        await aiofiles.os.remove(full_path)

        # Clean up empty parent directories
        dir_path = os.path.dirname(full_path)
        try:
            while dir_path != self.base_path:
                if os.listdir(dir_path):
                    break
                await aiofiles.os.rmdir(dir_path)
                dir_path = os.path.dirname(dir_path)
        except OSError:
            pass  # Directory not empty or other issue, ignore

        return True

    async def exists(self, key: str) -> bool:
        full_path = self._full_path(key)
        return os.path.exists(full_path)


class S3Storage(StorageBackend):
    """Store files in S3-compatible object storage.

    Suitable for production deployments. Works with AWS S3, MinIO,
    and other S3-compatible services.

    Requires the 'aioboto3' package to be installed.
    """

    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key

    def _get_client_kwargs(self) -> dict:
        """Build boto3 client kwargs."""
        kwargs: dict = {
            "region_name": self.region,
        }
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        if self.access_key and self.secret_key:
            kwargs["aws_access_key_id"] = self.access_key
            kwargs["aws_secret_access_key"] = self.secret_key
        return kwargs

    async def put(self, key: str, data: BinaryIO, content_type: str) -> str:
        import aioboto3

        session = aioboto3.Session()
        async with session.client("s3", **self._get_client_kwargs()) as s3:
            await s3.upload_fileobj(
                data,
                self.bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
        return key

    async def get(self, key: str) -> BinaryIO:
        import aioboto3

        session = aioboto3.Session()
        async with session.client("s3", **self._get_client_kwargs()) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket, Key=key)
                content = await response["Body"].read()
                return BytesIO(content)
            except s3.exceptions.NoSuchKey:
                raise FileNotFoundError(f"File not found in S3: {key}")

    async def delete(self, key: str) -> bool:
        import aioboto3

        session = aioboto3.Session()
        async with session.client("s3", **self._get_client_kwargs()) as s3:
            try:
                await s3.delete_object(Bucket=self.bucket, Key=key)
                return True
            except Exception:
                return False

    async def exists(self, key: str) -> bool:
        import aioboto3

        session = aioboto3.Session()
        async with session.client("s3", **self._get_client_kwargs()) as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=key)
                return True
            except Exception:
                return False


def get_storage_backend(
    backend_type: str = "local",
    base_path: str = "/tmp/docservice/attachments",
    s3_bucket: str = "",
    s3_region: str = "us-east-1",
    s3_endpoint_url: str = "",
    s3_access_key: str = "",
    s3_secret_key: str = "",
) -> StorageBackend:
    """Factory function to create the appropriate storage backend.

    Args:
        backend_type: "local" or "s3"
        base_path: Base directory for local storage
        s3_bucket: S3 bucket name
        s3_region: AWS region
        s3_endpoint_url: Custom S3 endpoint (for MinIO)
        s3_access_key: AWS access key
        s3_secret_key: AWS secret key

    Returns:
        Configured StorageBackend instance
    """
    if backend_type == "s3":
        return S3Storage(
            bucket=s3_bucket,
            region=s3_region,
            endpoint_url=s3_endpoint_url or None,
            access_key=s3_access_key or None,
            secret_key=s3_secret_key or None,
        )
    return LocalFilesystemStorage(base_path=base_path)
