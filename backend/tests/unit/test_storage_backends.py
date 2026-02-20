"""Unit tests for storage backends.

Sprint F: Attachments & Media Support
"""

import os
import tempfile
from io import BytesIO

import pytest

from src.modules.attachments.storage import (
    LocalFilesystemStorage,
    S3Storage,
    get_storage_backend,
)


class TestLocalFilesystemStorage:
    """Test LocalFilesystemStorage backend."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create a local storage instance with temp directory."""
        return LocalFilesystemStorage(base_path=str(tmp_path))

    @pytest.fixture
    def sample_data(self):
        """Create sample file data."""
        return BytesIO(b"Hello, this is test file content!")

    @pytest.mark.asyncio
    async def test_put_and_get(self, storage, sample_data):
        """Test storing and retrieving a file."""
        key = "org1/page1/att1/v1/test.txt"
        await storage.put(key, sample_data, "text/plain")

        result = await storage.get(key)
        content = result.read()
        assert content == b"Hello, this is test file content!"

    @pytest.mark.asyncio
    async def test_put_creates_directories(self, storage, sample_data):
        """Test that put creates necessary directories."""
        key = "deep/nested/path/to/file.txt"
        await storage.put(key, sample_data, "text/plain")

        assert await storage.exists(key)

    @pytest.mark.asyncio
    async def test_exists_true(self, storage, sample_data):
        """Test exists returns True for stored files."""
        key = "org1/page1/att1/v1/test.txt"
        await storage.put(key, sample_data, "text/plain")

        assert await storage.exists(key) is True

    @pytest.mark.asyncio
    async def test_exists_false(self, storage):
        """Test exists returns False for non-existent files."""
        assert await storage.exists("nonexistent/file.txt") is False

    @pytest.mark.asyncio
    async def test_delete(self, storage, sample_data):
        """Test deleting a file."""
        key = "org1/page1/att1/v1/test.txt"
        await storage.put(key, sample_data, "text/plain")

        result = await storage.delete(key)
        assert result is True
        assert await storage.exists(key) is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, storage):
        """Test deleting a non-existent file returns False."""
        result = await storage.delete("nonexistent/file.txt")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self, storage):
        """Test getting a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            await storage.get("nonexistent/file.txt")

    @pytest.mark.asyncio
    async def test_large_file(self, storage):
        """Test storing a larger file (1MB)."""
        data = BytesIO(b"x" * (1024 * 1024))
        key = "org1/page1/att1/v1/large.bin"
        await storage.put(key, data, "application/octet-stream")

        result = await storage.get(key)
        content = result.read()
        assert len(content) == 1024 * 1024

    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, storage, sample_data):
        """Test that path traversal attempts are neutralized."""
        key = "../../../etc/passwd"
        await storage.put(key, sample_data, "text/plain")

        # File should be stored within the base path
        full_path = storage._full_path(key)
        assert full_path.startswith(storage.base_path)

    @pytest.mark.asyncio
    async def test_multiple_files(self, storage):
        """Test storing multiple files."""
        for i in range(5):
            data = BytesIO(f"File content {i}".encode())
            await storage.put(f"org1/page1/att{i}/v1/file{i}.txt", data, "text/plain")

        for i in range(5):
            assert await storage.exists(f"org1/page1/att{i}/v1/file{i}.txt")


class TestGetStorageBackend:
    """Test the storage backend factory function."""

    def test_default_returns_local(self):
        """Test default returns LocalFilesystemStorage."""
        backend = get_storage_backend()
        assert isinstance(backend, LocalFilesystemStorage)

    def test_local_with_custom_path(self):
        """Test creating local storage with custom path."""
        backend = get_storage_backend(backend_type="local", base_path="/custom/path")
        assert isinstance(backend, LocalFilesystemStorage)
        assert backend.base_path == "/custom/path"

    def test_s3_backend(self):
        """Test creating S3 storage backend."""
        backend = get_storage_backend(
            backend_type="s3",
            s3_bucket="my-bucket",
            s3_region="eu-west-1",
            s3_endpoint_url="http://localhost:9000",
            s3_access_key="minioadmin",
            s3_secret_key="minioadmin",
        )
        assert isinstance(backend, S3Storage)
        assert backend.bucket == "my-bucket"
        assert backend.region == "eu-west-1"
        assert backend.endpoint_url == "http://localhost:9000"

    def test_s3_empty_endpoint_becomes_none(self):
        """Test that empty endpoint URL becomes None for AWS S3."""
        backend = get_storage_backend(
            backend_type="s3",
            s3_bucket="my-bucket",
            s3_endpoint_url="",
        )
        assert isinstance(backend, S3Storage)
        assert backend.endpoint_url is None
