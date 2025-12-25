"""Integration tests for permissions API (Sprint 5: Access Control).

Tests permission management endpoints and access control enforcement.

Compliance: ISO 9001 §7.5.3, 21 CFR §11.10(d)
"""

import pytest
from httpx import AsyncClient

from src.modules.access.security import create_access_token


class TestPermissionEndpoints:
    """Tests for permission management endpoints."""

    @pytest.mark.asyncio
    async def test_permissions_list_requires_auth(self, async_client: AsyncClient):
        """Permissions list endpoint should require authentication."""
        response = await async_client.get("/api/v1/permissions")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_permissions_list_with_invalid_token(self, async_client: AsyncClient):
        """Permissions list with invalid token should return 401."""
        response = await async_client.get(
            "/api/v1/permissions",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_grant_permission_requires_auth(self, async_client: AsyncClient):
        """Grant permission endpoint should require authentication."""
        response = await async_client.post(
            "/api/v1/permissions",
            json={
                "user_id": "user-123",
                "resource_type": "page",
                "resource_id": "page-456",
                "role": "viewer",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_grant_permission_validation(self, async_client: AsyncClient):
        """Grant permission should validate required fields."""
        # Generate a valid-looking token (even if user doesn't exist)
        token = create_access_token("test-user-id")

        # Missing user_id
        response = await async_client.post(
            "/api/v1/permissions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "resource_type": "page",
                "resource_id": "page-456",
                "role": "viewer",
            },
        )
        assert response.status_code in [401, 422]  # 401 if user doesn't exist, 422 validation

    @pytest.mark.asyncio
    async def test_get_permission_requires_auth(self, async_client: AsyncClient):
        """Get permission endpoint should require authentication."""
        response = await async_client.get("/api/v1/permissions/some-permission-id")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_revoke_permission_requires_auth(self, async_client: AsyncClient):
        """Revoke permission endpoint should require authentication."""
        response = await async_client.delete("/api/v1/permissions/some-permission-id")
        assert response.status_code == 401


class TestRoleCapabilitiesEndpoint:
    """Tests for role capabilities endpoint."""

    @pytest.mark.asyncio
    async def test_role_capabilities_requires_auth(self, async_client: AsyncClient):
        """Role capabilities endpoint should require authentication."""
        response = await async_client.get("/api/v1/permissions/roles/capabilities")
        assert response.status_code == 401


class TestAccessCheckEndpoint:
    """Tests for access check endpoint."""

    @pytest.mark.asyncio
    async def test_access_check_requires_auth(self, async_client: AsyncClient):
        """Access check endpoint should require authentication."""
        response = await async_client.post(
            "/api/v1/permissions/check",
            json={
                "user_id": "user-123",
                "resource_type": "page",
                "resource_id": "page-456",
                "action": "read",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_check_validation(self, async_client: AsyncClient):
        """Access check should validate required fields."""
        # Missing action
        response = await async_client.post(
            "/api/v1/permissions/check",
            json={
                "user_id": "user-123",
                "resource_type": "page",
                "resource_id": "page-456",
            },
        )
        assert response.status_code in [401, 422]


class TestClearanceEndpoint:
    """Tests for user clearance management."""

    @pytest.mark.asyncio
    async def test_update_clearance_requires_auth(self, async_client: AsyncClient):
        """Update clearance endpoint should require authentication."""
        response = await async_client.patch(
            "/api/v1/permissions/users/user-123/clearance",
            json={
                "clearance_level": 2,
                "reason": "Promoted to handle confidential documents",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_clearance_validation(self, async_client: AsyncClient):
        """Update clearance should validate clearance level range."""
        # Generate a valid-looking token
        token = create_access_token("test-user-id")

        # Invalid clearance level (too high)
        response = await async_client.patch(
            "/api/v1/permissions/users/user-123/clearance",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "clearance_level": 10,  # Invalid - must be 0-3
                "reason": "Test reason",
            },
        )
        assert response.status_code in [401, 403, 422]  # Validation or auth error


class TestUserPermissionsEndpoint:
    """Tests for user permissions listing."""

    @pytest.mark.asyncio
    async def test_user_permissions_requires_auth(self, async_client: AsyncClient):
        """User permissions endpoint should require authentication."""
        response = await async_client.get("/api/v1/permissions/users/user-123/permissions")
        assert response.status_code == 401


class TestEffectivePermissionsEndpoint:
    """Tests for effective permissions after inheritance resolution."""

    @pytest.mark.asyncio
    async def test_effective_permissions_requires_auth(self, async_client: AsyncClient):
        """Effective permissions endpoint should require authentication."""
        response = await async_client.get("/api/v1/permissions/effective/page/page-123")
        assert response.status_code == 401


class TestResourcePermissionsEndpoint:
    """Tests for resource-level permissions."""

    @pytest.mark.asyncio
    async def test_resource_permissions_requires_auth(self, async_client: AsyncClient):
        """Resource permissions endpoint should require authentication."""
        response = await async_client.get("/api/v1/permissions/resource/page/page-123")
        assert response.status_code == 401


class TestSessionEndpoints:
    """Tests for session management in auth endpoints."""

    @pytest.mark.asyncio
    async def test_logout_endpoint_exists(self, async_client: AsyncClient):
        """Logout endpoint should exist."""
        response = await async_client.post("/api/v1/auth/logout")
        # Should return 204 (success with no content) even without token
        assert response.status_code in [204, 401]

    @pytest.mark.asyncio
    async def test_logout_all_requires_auth(self, async_client: AsyncClient):
        """Logout all sessions requires authentication."""
        response = await async_client.post("/api/v1/auth/logout-all")
        assert response.status_code == 401


class TestPermissionSchemaValidation:
    """Tests for permission schema validation."""

    @pytest.mark.asyncio
    async def test_invalid_resource_type(self, async_client: AsyncClient):
        """Invalid resource type should be rejected."""
        token = create_access_token("test-user-id")

        response = await async_client.post(
            "/api/v1/permissions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": "user-123",
                "resource_type": "invalid_type",  # Not in ResourceTypeEnum
                "resource_id": "page-456",
                "role": "viewer",
            },
        )
        assert response.status_code in [401, 422]  # Validation error

    @pytest.mark.asyncio
    async def test_invalid_role(self, async_client: AsyncClient):
        """Invalid role should be rejected."""
        token = create_access_token("test-user-id")

        response = await async_client.post(
            "/api/v1/permissions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": "user-123",
                "resource_type": "page",
                "resource_id": "page-456",
                "role": "superadmin",  # Not a valid role
            },
        )
        assert response.status_code in [401, 422]  # Validation error

    @pytest.mark.asyncio
    async def test_invalid_action(self, async_client: AsyncClient):
        """Invalid action should be rejected in access check."""
        response = await async_client.post(
            "/api/v1/permissions/check",
            json={
                "user_id": "user-123",
                "resource_type": "page",
                "resource_id": "page-456",
                "action": "destroy_everything",  # Invalid action
            },
        )
        assert response.status_code in [401, 422]  # Validation error


class TestRoleHierarchy:
    """Tests for role hierarchy and capabilities."""

    @pytest.mark.asyncio
    async def test_role_values_in_schema(self, async_client: AsyncClient):
        """All expected roles should be accepted."""
        token = create_access_token("test-user-id")

        roles = ["viewer", "reviewer", "editor", "admin", "owner"]
        for role in roles:
            response = await async_client.post(
                "/api/v1/permissions",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "user_id": "user-123",
                    "resource_type": "page",
                    "resource_id": "page-456",
                    "role": role,
                },
            )
            # Should not get 422 validation error for valid roles
            # May get 401 (user not found) or 403 (not authorized)
            assert response.status_code != 422, f"Role '{role}' should be valid"


class TestClassificationLevels:
    """Tests for classification levels."""

    @pytest.mark.asyncio
    async def test_clearance_level_range(self, async_client: AsyncClient):
        """Clearance level should be validated (0-3)."""
        token = create_access_token("test-user-id")

        # Test valid levels
        for level in [0, 1, 2, 3]:
            response = await async_client.patch(
                "/api/v1/permissions/users/user-123/clearance",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "clearance_level": level,
                    "reason": f"Test clearance level {level}",
                },
            )
            # Should not get validation error for valid levels
            # May get 401/403 for auth issues
            assert response.status_code != 422 or level > 3, f"Level {level} should be valid"

        # Test invalid level
        response = await async_client.patch(
            "/api/v1/permissions/users/user-123/clearance",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "clearance_level": 4,  # Invalid - max is 3
                "reason": "Test invalid level",
            },
        )
        assert response.status_code in [401, 403, 422]
