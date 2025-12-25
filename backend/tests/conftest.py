"""Pytest configuration and fixtures for backend tests."""

import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before importing app modules
os.environ["ENVIRONMENT"] = "development"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["GIT_REPOS_PATH"] = tempfile.mkdtemp()
os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://localhost:3000"

from src.db.base import Base
from src.api.deps import get_db
from src.main import create_app
from src.modules.access.security import hash_password, create_access_token


# Use SQLite for testing (in-memory)
SQLITE_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        SQLITE_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for each test with proper isolation.

    Uses nested transactions (savepoints) to ensure each test is isolated
    and changes are rolled back after each test.
    """
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_engine.connect() as connection:
        # Start an outer transaction that we'll roll back
        await connection.begin()

        # Create a session bound to this connection
        async_session = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with async_session() as session:
            yield session

        # Rollback the outer transaction to undo all test changes
        await connection.rollback()


@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    """Create FastAPI app for testing."""
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def git_temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for Git repositories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# Test data fixtures

@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user registration data."""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "SecureP@ssw0rd!",
        "title": "Developer",
    }


@pytest.fixture
def sample_org_data() -> dict[str, Any]:
    """Sample organization data."""
    return {
        "name": "Test Organization",
        "slug": "test-org",
        "description": "A test organization",
    }


@pytest.fixture
def sample_workspace_data() -> dict[str, Any]:
    """Sample workspace data."""
    return {
        "name": "Test Workspace",
        "slug": "test-workspace",
        "description": "A test workspace",
        "is_public": False,
    }


@pytest.fixture
def sample_space_data() -> dict[str, Any]:
    """Sample space data."""
    return {
        "name": "Test Space",
        "slug": "test-space",
        "description": "A test space",
        "diataxis_type": "tutorial",
    }


@pytest.fixture
def sample_page_data() -> dict[str, Any]:
    """Sample page data."""
    return {
        "title": "Test Page",
        "slug": "test-page",
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello, world!"}]
                }
            ]
        },
        "summary": "A test page",
    }


@pytest.fixture
def sample_page_content() -> dict[str, Any]:
    """Sample TipTap editor content."""
    return {
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": "Getting Started"}]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "This is a "},
                    {"type": "text", "marks": [{"type": "bold"}], "text": "test"},
                    {"type": "text", "text": " document."}
                ]
            },
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [
                            {"type": "paragraph", "content": [{"type": "text", "text": "Item 1"}]}
                        ]
                    },
                    {
                        "type": "listItem",
                        "content": [
                            {"type": "paragraph", "content": [{"type": "text", "text": "Item 2"}]}
                        ]
                    },
                ]
            },
        ]
    }


# Mock fixtures for external services

@pytest.fixture
def mock_meilisearch():
    """Mock Meilisearch client."""
    mock = MagicMock()
    mock.index.return_value.search.return_value = {
        "hits": [],
        "estimatedTotalHits": 0,
        "processingTimeMs": 1,
    }
    mock.index.return_value.add_documents.return_value = {"taskUid": 1}
    mock.index.return_value.delete_document.return_value = {"taskUid": 2}
    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    return mock


@pytest.fixture
def mock_git_service():
    """Mock Git service for integration tests.

    This provides a mock that simulates Git operations without
    requiring an actual Git repository.
    """
    mock = MagicMock()

    # Track branches that have been created
    branches = set()
    commit_counter = 0
    # Track branches with simulated conflicts
    conflict_branches = set()

    def create_branch_side_effect(org_slug, branch_name, from_ref="HEAD"):
        branches.add(branch_name)
        return True

    def list_branches_side_effect(org_slug):
        return list(branches)

    def delete_branch_side_effect(org_slug, branch_name):
        if branch_name in branches:
            branches.discard(branch_name)
            return True
        return False

    def generate_commit_sha():
        nonlocal commit_counter
        commit_counter += 1
        return f"commit{commit_counter:040d}"

    def update_file_side_effect(
        org_slug, workspace_slug, space_slug, page_slug, content,
        author_name, author_email, message, branch=None
    ):
        return generate_commit_sha()

    def create_file_side_effect(
        org_slug, workspace_slug, space_slug, page_slug, content,
        author_name, author_email, message
    ):
        return generate_commit_sha()

    def merge_branch_side_effect(
        org_slug, source_branch, target_branch, author_name, author_email, message
    ):
        # Simulate conflict if branch is marked for conflict
        if source_branch in conflict_branches:
            return None
        if source_branch in branches:
            return generate_commit_sha()
        return None

    def check_merge_conflicts_side_effect(org_slug, source_branch, target_branch):
        # Return conflict status
        if source_branch in conflict_branches:
            return {
                "has_conflicts": True,
                "conflict_files": ["content.json"],
                "can_fast_forward": False,
            }
        return {
            "has_conflicts": False,
            "conflict_files": [],
            "can_fast_forward": source_branch in branches,
        }

    # Helper method to simulate conflicts (for tests)
    def simulate_conflict(branch_name):
        conflict_branches.add(branch_name)

    def clear_conflict(branch_name):
        conflict_branches.discard(branch_name)

    mock.create_branch.side_effect = create_branch_side_effect
    mock.list_branches.side_effect = list_branches_side_effect
    mock.delete_branch.side_effect = delete_branch_side_effect
    mock.update_file.side_effect = update_file_side_effect
    mock.create_file.side_effect = create_file_side_effect
    mock.merge_branch.side_effect = merge_branch_side_effect
    mock.check_merge_conflicts.side_effect = check_merge_conflicts_side_effect
    mock.init_repo.return_value = True
    mock.get_repo.return_value = MagicMock()  # Return a mock repo object
    mock.read_file.return_value = {"type": "doc", "content": []}
    mock.get_file_history.return_value = []

    # Expose helper methods for tests
    mock._simulate_conflict = simulate_conflict
    mock._clear_conflict = clear_conflict
    mock._conflict_branches = conflict_branches

    return mock


@pytest.fixture
def patch_git_service(mock_git_service):
    """Patch the git service singleton to use the mock."""
    import src.modules.content.git_service as git_module

    original_service = git_module._git_service
    git_module._git_service = mock_git_service

    yield mock_git_service

    # Restore original
    git_module._git_service = original_service
