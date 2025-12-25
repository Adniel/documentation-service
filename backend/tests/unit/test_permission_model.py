"""Unit tests for Permission model and Role enum (Sprint 5)."""

import pytest
from datetime import datetime, timedelta

from src.db.models.permission import (
    Permission,
    Role,
    ResourceType,
    ClassificationLevel,
    ROLE_CAPABILITIES,
)


class TestRoleEnum:
    """Tests for Role enum."""

    def test_role_hierarchy_values(self):
        """Roles should have correct hierarchy values."""
        assert Role.VIEWER.value == 1
        assert Role.REVIEWER.value == 2
        assert Role.EDITOR.value == 3
        assert Role.ADMIN.value == 4
        assert Role.OWNER.value == 5

    def test_role_from_string(self):
        """Should convert string to Role enum."""
        assert Role.from_string("viewer") == Role.VIEWER
        assert Role.from_string("ADMIN") == Role.ADMIN
        assert Role.from_string("Owner") == Role.OWNER

    def test_role_to_string(self):
        """Should convert Role enum to lowercase string."""
        assert str(Role.VIEWER) == "viewer"
        assert str(Role.ADMIN) == "admin"
        assert str(Role.OWNER) == "owner"

    def test_can_perform_same_role(self):
        """Role should be able to perform its own level."""
        assert Role.VIEWER.can_perform(Role.VIEWER) is True
        assert Role.ADMIN.can_perform(Role.ADMIN) is True
        assert Role.OWNER.can_perform(Role.OWNER) is True

    def test_can_perform_lower_role(self):
        """Higher roles can perform lower role actions."""
        assert Role.ADMIN.can_perform(Role.VIEWER) is True
        assert Role.ADMIN.can_perform(Role.EDITOR) is True
        assert Role.OWNER.can_perform(Role.ADMIN) is True
        assert Role.EDITOR.can_perform(Role.REVIEWER) is True

    def test_cannot_perform_higher_role(self):
        """Lower roles cannot perform higher role actions."""
        assert Role.VIEWER.can_perform(Role.EDITOR) is False
        assert Role.REVIEWER.can_perform(Role.ADMIN) is False
        assert Role.EDITOR.can_perform(Role.OWNER) is False
        assert Role.ADMIN.can_perform(Role.OWNER) is False


class TestClassificationLevel:
    """Tests for ClassificationLevel enum."""

    def test_classification_hierarchy_values(self):
        """Classification levels should have correct values."""
        assert ClassificationLevel.PUBLIC.value == 0
        assert ClassificationLevel.INTERNAL.value == 1
        assert ClassificationLevel.CONFIDENTIAL.value == 2
        assert ClassificationLevel.RESTRICTED.value == 3

    def test_classification_from_string(self):
        """Should convert string to ClassificationLevel enum."""
        assert ClassificationLevel.from_string("public") == ClassificationLevel.PUBLIC
        assert ClassificationLevel.from_string("CONFIDENTIAL") == ClassificationLevel.CONFIDENTIAL

    def test_classification_comparison(self):
        """Classification levels should be comparable."""
        assert ClassificationLevel.PUBLIC < ClassificationLevel.INTERNAL
        assert ClassificationLevel.INTERNAL < ClassificationLevel.CONFIDENTIAL
        assert ClassificationLevel.CONFIDENTIAL < ClassificationLevel.RESTRICTED


class TestRoleCapabilities:
    """Tests for role capabilities mapping."""

    def test_viewer_capabilities(self):
        """Viewer should only be able to read."""
        caps = ROLE_CAPABILITIES[Role.VIEWER]
        assert caps["can_read"] is True
        assert caps["can_comment"] is False
        assert caps["can_edit"] is False
        assert caps["can_approve"] is False
        assert caps["can_manage_members"] is False

    def test_reviewer_capabilities(self):
        """Reviewer can read, comment, and approve."""
        caps = ROLE_CAPABILITIES[Role.REVIEWER]
        assert caps["can_read"] is True
        assert caps["can_comment"] is True
        assert caps["can_edit"] is False
        assert caps["can_approve"] is True

    def test_editor_capabilities(self):
        """Editor can read, comment, edit, and delete own."""
        caps = ROLE_CAPABILITIES[Role.EDITOR]
        assert caps["can_read"] is True
        assert caps["can_comment"] is True
        assert caps["can_edit"] is True
        assert caps["can_delete_own"] is True
        assert caps["can_delete_any"] is False
        assert caps["can_approve"] is False

    def test_admin_capabilities(self):
        """Admin can do everything except delete resource."""
        caps = ROLE_CAPABILITIES[Role.ADMIN]
        assert caps["can_read"] is True
        assert caps["can_edit"] is True
        assert caps["can_delete_any"] is True
        assert caps["can_approve"] is True
        assert caps["can_manage_members"] is True
        assert caps["can_manage_settings"] is True
        assert caps["can_delete_resource"] is False

    def test_owner_capabilities(self):
        """Owner can do everything."""
        caps = ROLE_CAPABILITIES[Role.OWNER]
        assert caps["can_read"] is True
        assert caps["can_edit"] is True
        assert caps["can_delete_any"] is True
        assert caps["can_approve"] is True
        assert caps["can_manage_members"] is True
        assert caps["can_manage_settings"] is True
        assert caps["can_delete_resource"] is True


class TestPermissionModel:
    """Tests for Permission model."""

    def test_permission_role_enum_property(self):
        """Should convert role int to enum."""
        perm = Permission(
            user_id="user-1",
            resource_type=ResourceType.PAGE,
            resource_id="page-1",
            role=Role.EDITOR.value,
            granted_by_id="admin-1",
        )
        assert perm.role_enum == Role.EDITOR

    def test_permission_is_valid_active(self):
        """Active permission without expiry should be valid."""
        perm = Permission(
            user_id="user-1",
            resource_type=ResourceType.PAGE,
            resource_id="page-1",
            role=Role.VIEWER.value,
            granted_by_id="admin-1",
            is_active=True,
            expires_at=None,
        )
        assert perm.is_valid() is True

    def test_permission_is_valid_inactive(self):
        """Inactive permission should not be valid."""
        perm = Permission(
            user_id="user-1",
            resource_type=ResourceType.PAGE,
            resource_id="page-1",
            role=Role.VIEWER.value,
            granted_by_id="admin-1",
            is_active=False,
        )
        assert perm.is_valid() is False

    def test_permission_is_valid_expired(self):
        """Expired permission should not be valid."""
        perm = Permission(
            user_id="user-1",
            resource_type=ResourceType.PAGE,
            resource_id="page-1",
            role=Role.VIEWER.value,
            granted_by_id="admin-1",
            is_active=True,
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert perm.is_valid() is False

    def test_permission_is_valid_not_expired(self):
        """Permission with future expiry should be valid."""
        perm = Permission(
            user_id="user-1",
            resource_type=ResourceType.PAGE,
            resource_id="page-1",
            role=Role.VIEWER.value,
            granted_by_id="admin-1",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert perm.is_valid() is True

    def test_permission_can_perform(self):
        """Permission should check role level."""
        perm = Permission(
            user_id="user-1",
            resource_type=ResourceType.PAGE,
            resource_id="page-1",
            role=Role.EDITOR.value,
            granted_by_id="admin-1",
            is_active=True,
        )
        assert perm.can_perform(Role.VIEWER) is True
        assert perm.can_perform(Role.EDITOR) is True
        assert perm.can_perform(Role.ADMIN) is False

    def test_permission_repr(self):
        """Permission should have readable repr."""
        perm = Permission(
            user_id="user-123",
            resource_type=ResourceType.PAGE,
            resource_id="page-456",
            role=Role.EDITOR.value,
            granted_by_id="admin-1",
        )
        repr_str = repr(perm)
        assert "user-123" in repr_str
        assert "page" in repr_str
        assert "editor" in repr_str.lower()  # Role appears in lowercase


class TestResourceType:
    """Tests for ResourceType constants."""

    def test_resource_types_exist(self):
        """All resource types should be defined."""
        assert ResourceType.ORGANIZATION == "organization"
        assert ResourceType.WORKSPACE == "workspace"
        assert ResourceType.SPACE == "space"
        assert ResourceType.PAGE == "page"
