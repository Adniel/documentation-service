"""Unit tests for Git service (Sprint 1)."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.modules.content.git_service import GitService


class TestGitServiceInit:
    """Tests for GitService initialization."""

    def test_init_creates_base_path(self, git_temp_dir: str):
        """Service should create base path if it doesn't exist."""
        new_path = os.path.join(git_temp_dir, "new", "nested", "path")
        service = GitService(new_path)

        assert os.path.exists(new_path)
        assert service.base_path == Path(new_path)

    def test_init_existing_path(self, git_temp_dir: str):
        """Service should work with existing path."""
        service = GitService(git_temp_dir)

        assert service.base_path == Path(git_temp_dir)


class TestGitServiceRepository:
    """Tests for repository operations."""

    def test_init_repo_creates_repository(self, git_temp_dir: str):
        """init_repo should create a new Git repository."""
        service = GitService(git_temp_dir)
        repo = service.init_repo("test-org")

        assert repo is not None
        repo_path = os.path.join(git_temp_dir, "test-org")
        assert os.path.exists(repo_path)
        assert os.path.exists(os.path.join(repo_path, ".git"))

    def test_init_repo_creates_initial_commit(self, git_temp_dir: str):
        """init_repo should create an initial commit with README."""
        service = GitService(git_temp_dir)
        repo = service.init_repo("test-org")

        # Check that HEAD exists and has a commit
        assert not repo.head_is_unborn
        assert repo.head.peel().message == "Initial repository setup"

        # Check README exists
        readme_path = os.path.join(git_temp_dir, "test-org", "README.md")
        assert os.path.exists(readme_path)

    def test_init_repo_idempotent(self, git_temp_dir: str):
        """init_repo should return existing repo if already initialized."""
        service = GitService(git_temp_dir)
        repo1 = service.init_repo("test-org")
        repo2 = service.init_repo("test-org")

        assert repo1 is not None
        assert repo2 is not None

    def test_get_repo_existing(self, git_temp_dir: str):
        """get_repo should return existing repository."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        repo = service.get_repo("test-org")

        assert repo is not None

    def test_get_repo_nonexistent(self, git_temp_dir: str):
        """get_repo should return None for non-existent repo."""
        service = GitService(git_temp_dir)

        repo = service.get_repo("nonexistent-org")

        assert repo is None


class TestGitServiceFileOperations:
    """Tests for file CRUD operations."""

    def test_create_file(self, git_temp_dir: str):
        """create_file should create file and commit."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        content = {"title": "Test Page", "body": "Hello, world!"}
        commit_sha = service.create_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content=content,
            author_name="Test User",
            author_email="test@example.com",
        )

        assert commit_sha is not None
        assert len(commit_sha) == 40  # Git SHA-1 length

        # Verify file exists
        file_path = os.path.join(
            git_temp_dir, "test-org", "workspace", "space", "page.json"
        )
        assert os.path.exists(file_path)

        # Verify content
        with open(file_path, "r") as f:
            saved_content = json.load(f)
        assert saved_content == content

    def test_create_file_creates_directories(self, git_temp_dir: str):
        """create_file should create necessary directories."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        service.create_file(
            org_slug="test-org",
            workspace_slug="deep/nested/workspace",
            space_slug="space",
            page_slug="page",
            content={"test": "data"},
            author_name="Test User",
            author_email="test@example.com",
        )

        dir_path = os.path.join(
            git_temp_dir, "test-org", "deep/nested/workspace", "space"
        )
        assert os.path.exists(dir_path)

    def test_read_file(self, git_temp_dir: str):
        """read_file should return file content."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        content = {"title": "Test Page", "body": "Content here"}
        service.create_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content=content,
            author_name="Test User",
            author_email="test@example.com",
        )

        result = service.read_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
        )

        assert result == content

    def test_read_file_nonexistent(self, git_temp_dir: str):
        """read_file should return None for non-existent file."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        result = service.read_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="nonexistent",
        )

        assert result is None

    def test_read_file_from_specific_commit(self, git_temp_dir: str):
        """read_file should return content from specific commit."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        # Create initial version
        content_v1 = {"version": 1, "title": "V1"}
        commit_v1 = service.create_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content=content_v1,
            author_name="Test User",
            author_email="test@example.com",
        )

        # Update to v2
        content_v2 = {"version": 2, "title": "V2"}
        service.update_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content=content_v2,
            author_name="Test User",
            author_email="test@example.com",
        )

        # Read from v1 commit
        result = service.read_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            commit_sha=commit_v1,
        )

        assert result == content_v1

    def test_update_file(self, git_temp_dir: str):
        """update_file should update existing file."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        # Create file
        service.create_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content={"version": 1},
            author_name="Test User",
            author_email="test@example.com",
        )

        # Update file
        new_content = {"version": 2, "updated": True}
        commit_sha = service.update_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content=new_content,
            author_name="Test User",
            author_email="test@example.com",
        )

        assert commit_sha is not None

        # Verify updated content
        result = service.read_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
        )
        assert result == new_content

    def test_update_file_nonexistent_raises(self, git_temp_dir: str):
        """update_file should raise for non-existent file."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        with pytest.raises(FileNotFoundError):
            service.update_file(
                org_slug="test-org",
                workspace_slug="workspace",
                space_slug="space",
                page_slug="nonexistent",
                content={"test": "data"},
                author_name="Test User",
                author_email="test@example.com",
            )

    def test_update_file_nonexistent_repo_raises(self, git_temp_dir: str):
        """update_file should raise for non-existent repo."""
        service = GitService(git_temp_dir)

        with pytest.raises(ValueError, match="Repository not found"):
            service.update_file(
                org_slug="nonexistent-org",
                workspace_slug="workspace",
                space_slug="space",
                page_slug="page",
                content={"test": "data"},
                author_name="Test User",
                author_email="test@example.com",
            )


class TestGitServiceHistory:
    """Tests for file history operations."""

    def test_get_file_history(self, git_temp_dir: str):
        """get_file_history should return commit history."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        # Create file
        service.create_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content={"version": 1},
            author_name="Test User",
            author_email="test@example.com",
            message="Create page",
        )

        # Update file
        service.update_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content={"version": 2},
            author_name="Test User",
            author_email="test@example.com",
            message="Update page",
        )

        history = service.get_file_history(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
        )

        assert len(history) == 2
        assert history[0]["message"] == "Update page"
        assert history[1]["message"] == "Create page"
        assert "sha" in history[0]
        assert "author_name" in history[0]
        assert "timestamp" in history[0]

    def test_get_file_history_limit(self, git_temp_dir: str):
        """get_file_history should respect limit parameter."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        # Create and update file multiple times
        service.create_file(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            content={"version": 1},
            author_name="Test User",
            author_email="test@example.com",
        )

        for i in range(5):
            service.update_file(
                org_slug="test-org",
                workspace_slug="workspace",
                space_slug="space",
                page_slug="page",
                content={"version": i + 2},
                author_name="Test User",
                author_email="test@example.com",
            )

        history = service.get_file_history(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="page",
            limit=3,
        )

        assert len(history) == 3

    def test_get_file_history_nonexistent(self, git_temp_dir: str):
        """get_file_history should return empty list for non-existent file."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        history = service.get_file_history(
            org_slug="test-org",
            workspace_slug="workspace",
            space_slug="space",
            page_slug="nonexistent",
        )

        assert history == []


class TestGitServiceBranches:
    """Tests for branch operations."""

    def test_create_branch(self, git_temp_dir: str):
        """create_branch should create a new branch."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        result = service.create_branch("test-org", "feature-branch")

        assert result is True

        branches = service.list_branches("test-org")
        assert "feature-branch" in branches

    def test_create_branch_nonexistent_repo(self, git_temp_dir: str):
        """create_branch should return False for non-existent repo."""
        service = GitService(git_temp_dir)

        result = service.create_branch("nonexistent-org", "feature-branch")

        assert result is False

    def test_list_branches(self, git_temp_dir: str):
        """list_branches should return all local branches."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")
        service.create_branch("test-org", "branch-1")
        service.create_branch("test-org", "branch-2")

        branches = service.list_branches("test-org")

        assert "master" in branches or "main" in branches
        assert "branch-1" in branches
        assert "branch-2" in branches

    def test_delete_branch(self, git_temp_dir: str):
        """delete_branch should remove a branch."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")
        service.create_branch("test-org", "temp-branch")

        result = service.delete_branch("test-org", "temp-branch")

        assert result is True

        branches = service.list_branches("test-org")
        assert "temp-branch" not in branches

    def test_delete_branch_nonexistent(self, git_temp_dir: str):
        """delete_branch should return False for non-existent branch."""
        service = GitService(git_temp_dir)
        service.init_repo("test-org")

        result = service.delete_branch("test-org", "nonexistent-branch")

        assert result is False
