"""Unit tests for CLI seed module (Sprint H)."""

import argparse
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.cli.fixtures import DEMO_FIXTURE, MINIMAL_FIXTURE


class TestFixtures:
    """Tests for fixture data structure and integrity."""

    def test_minimal_fixture_has_required_keys(self):
        """Minimal fixture must have users, organization, workspaces, pages."""
        assert "users" in MINIMAL_FIXTURE
        assert "organization" in MINIMAL_FIXTURE
        assert "workspaces" in MINIMAL_FIXTURE
        assert "pages" in MINIMAL_FIXTURE

    def test_demo_fixture_has_required_keys(self):
        """Demo fixture must have users, organization, workspaces, pages."""
        assert "users" in DEMO_FIXTURE
        assert "organization" in DEMO_FIXTURE
        assert "workspaces" in DEMO_FIXTURE
        assert "pages" in DEMO_FIXTURE

    def test_minimal_fixture_has_one_user(self):
        """Minimal fixture should have exactly one admin user."""
        assert len(MINIMAL_FIXTURE["users"]) == 1
        user = MINIMAL_FIXTURE["users"][0]
        assert user["is_superuser"] is True
        assert user["clearance_level"] == 3

    def test_demo_fixture_has_three_users(self):
        """Demo fixture should have three users with varying roles."""
        assert len(DEMO_FIXTURE["users"]) == 3
        # First user should be admin/superuser
        assert DEMO_FIXTURE["users"][0]["is_superuser"] is True

    def test_minimal_fixture_has_no_pages(self):
        """Minimal fixture should have zero pages."""
        assert len(MINIMAL_FIXTURE["pages"]) == 0

    def test_demo_fixture_has_pages(self):
        """Demo fixture should have approximately 12 pages."""
        assert len(DEMO_FIXTURE["pages"]) >= 10

    def test_organization_has_valid_slug(self):
        """Organization slug must be lowercase with hyphens only."""
        for fixture in [MINIMAL_FIXTURE, DEMO_FIXTURE]:
            slug = fixture["organization"]["slug"]
            assert slug == slug.lower()
            assert all(c.isalnum() or c == "-" for c in slug)

    def test_all_pages_reference_valid_workspace_space(self):
        """Every page must reference a workspace_slug and space_slug that exist."""
        # Build a set of valid (workspace_slug, space_slug) pairs
        valid_pairs = set()
        for ws in DEMO_FIXTURE["workspaces"]:
            for sp in ws["spaces"]:
                valid_pairs.add((ws["slug"], sp["slug"]))

        for page in DEMO_FIXTURE["pages"]:
            pair = (page["workspace_slug"], page["space_slug"])
            assert pair in valid_pairs, (
                f"Page '{page['title']}' references invalid space: {pair}"
            )

    def test_all_users_have_required_fields(self):
        """Every user must have email, password, full_name."""
        for fixture in [MINIMAL_FIXTURE, DEMO_FIXTURE]:
            for user in fixture["users"]:
                assert "email" in user
                assert "password" in user
                assert "full_name" in user

    def test_all_pages_have_required_fields(self):
        """Every page must have title, slug, workspace_slug, space_slug."""
        for page in DEMO_FIXTURE["pages"]:
            assert "title" in page
            assert "slug" in page
            assert "workspace_slug" in page
            assert "space_slug" in page

    def test_page_slugs_are_valid(self):
        """Page slugs must be lowercase with hyphens only."""
        for page in DEMO_FIXTURE["pages"]:
            slug = page["slug"]
            assert slug == slug.lower(), f"Slug not lowercase: {slug}"
            assert all(c.isalnum() or c == "-" for c in slug), (
                f"Invalid slug characters: {slug}"
            )

    def test_page_content_is_tiptap_format(self):
        """Pages with content must have valid TipTap JSON structure."""
        for page in DEMO_FIXTURE["pages"]:
            content = page.get("content")
            if content is not None:
                assert isinstance(content, dict)
                assert content.get("type") == "doc"
                assert "content" in content
                assert isinstance(content["content"], list)
                assert len(content["content"]) > 0

    def test_classification_values_are_valid(self):
        """Page classification must be a valid level."""
        valid = {"public", "internal", "confidential", "restricted"}
        for page in DEMO_FIXTURE["pages"]:
            classification = page.get("classification", "public")
            assert classification in valid, (
                f"Invalid classification '{classification}' on page '{page['title']}'"
            )

    def test_demo_fixture_has_mixed_classifications(self):
        """Demo fixture should have a mix of classification levels."""
        classifications = set()
        for page in DEMO_FIXTURE["pages"]:
            classifications.add(page.get("classification", "public"))
        # Should have at least public and one other
        assert "public" in classifications
        assert len(classifications) >= 2

    def test_all_workspaces_have_four_diataxis_spaces(self):
        """Each workspace should have exactly 4 spaces covering all Diataxis types."""
        expected_types = {"tutorial", "how_to", "reference", "explanation"}
        for fixture in [MINIMAL_FIXTURE, DEMO_FIXTURE]:
            for ws in fixture["workspaces"]:
                types = {sp["diataxis_type"] for sp in ws["spaces"]}
                assert types == expected_types, (
                    f"Workspace '{ws['name']}' has types {types}, expected {expected_types}"
                )

    def test_demo_fixture_has_two_workspaces(self):
        """Demo fixture should have exactly two workspaces."""
        assert len(DEMO_FIXTURE["workspaces"]) == 2


class TestCLIEntryPoint:
    """Tests for CLI argument parsing."""

    def test_seed_command_default_fixture(self):
        """Seed command should default to 'demo' fixture."""
        from src.cli.__main__ import main

        with patch("src.cli.__main__.argparse.ArgumentParser.parse_args") as mock_parse:
            mock_parse.return_value = argparse.Namespace(
                command="seed", fixture="demo", force=False
            )
            with patch("src.cli.__main__.asyncio") as mock_asyncio:
                with patch("src.cli.seed.seed_database") as mock_seed:
                    main()
                    mock_asyncio.run.assert_called_once()

    def test_no_command_shows_help(self):
        """Running without a command should show help and exit."""
        from src.cli.__main__ import main

        with patch("src.cli.__main__.argparse.ArgumentParser.parse_args") as mock_parse:
            mock_parse.return_value = argparse.Namespace(command=None)
            with patch("src.cli.__main__.argparse.ArgumentParser.print_help"):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1


class TestSeedDatabase:
    """Tests for the seed_database function logic."""

    @pytest.mark.asyncio
    async def test_seed_skips_existing_org_without_force(self):
        """Seed should exit if org exists and --force not provided."""
        from src.cli.seed import seed_database

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("src.cli.seed.async_session_maker", return_value=mock_session):
            with patch("src.cli.seed.get_organization_by_slug", return_value=MagicMock()):
                with pytest.raises(SystemExit) as exc_info:
                    await seed_database(fixture="minimal", force=False)
                assert exc_info.value.code == 1

    @pytest.mark.asyncio
    async def test_seed_creates_users_and_org(self):
        """Seed should create users and organization."""
        from src.cli.seed import seed_database

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_org = MagicMock()
        mock_org.id = "org-123"
        mock_org.name = "Acme Corp"
        mock_org.slug = "acme-corp"

        mock_workspace = MagicMock()
        mock_workspace.id = "ws-123"

        mock_space = MagicMock()
        mock_space.id = "sp-123"

        with patch("src.cli.seed.async_session_maker", return_value=mock_session):
            with patch("src.cli.seed.get_organization_by_slug", return_value=None):
                with patch("src.cli.seed.hash_password", return_value="hashed"):
                    with patch("src.cli.seed.create_organization", return_value=mock_org):
                        with patch("src.cli.seed.create_workspace", return_value=mock_workspace):
                            with patch("src.cli.seed.create_space", return_value=mock_space):
                                with patch("src.cli.seed.create_page", return_value=MagicMock()):
                                    with patch("src.cli.seed.get_git_service") as mock_git:
                                        mock_git_instance = MagicMock()
                                        mock_git.return_value = mock_git_instance
                                        await seed_database(
                                            fixture="minimal", force=False
                                        )

                                        # Verify git repo was initialized
                                        mock_git_instance.init_repo.assert_called_once_with(
                                            "acme-corp"
                                        )
                                        # Verify org was created
                                        assert mock_session.add.called
