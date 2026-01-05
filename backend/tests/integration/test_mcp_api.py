"""Integration tests for MCP API endpoints.

Sprint C: MCP Integration
"""

import pytest
from httpx import AsyncClient


class TestServiceAccountAPI:
    """Integration tests for service account endpoints."""

    @pytest.mark.asyncio
    async def test_create_service_account(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating a service account."""
        response = await async_client.post(
            "/api/v1/service-accounts",
            json={
                "name": "Test MCP Account",
                "description": "Test account for MCP integration",
                "role": "reader",
                "rate_limit_per_minute": 100,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test MCP Account"
        assert data["role"] == "reader"
        assert data["is_active"] is True
        assert "api_key" in data
        assert data["api_key"].startswith("dsk_")
        assert data["rate_limit_per_minute"] == 100

    @pytest.mark.asyncio
    async def test_create_service_account_with_restrictions(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test creating a service account with operation restrictions."""
        response = await async_client.post(
            "/api/v1/service-accounts",
            json={
                "name": "Restricted Account",
                "role": "reader",
                "allowed_operations": ["search_documents", "get_document"],
                "ip_allowlist": ["192.168.1.0/24"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["allowed_operations"] == ["search_documents", "get_document"]
        assert data["ip_allowlist"] == ["192.168.1.0/24"]

    @pytest.mark.asyncio
    async def test_list_service_accounts(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test listing service accounts."""
        # Create a few accounts first
        for i in range(3):
            await async_client.post(
                "/api/v1/service-accounts",
                json={"name": f"List Test Account {i}", "role": "reader"},
                headers=auth_headers,
            )

        response = await async_client.get(
            "/api/v1/service-accounts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert "total" in data
        assert len(data["accounts"]) >= 3

    @pytest.mark.asyncio
    async def test_list_service_accounts_include_inactive(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test listing service accounts including inactive ones."""
        # Create and deactivate an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "Inactive Account", "role": "reader"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]

        await async_client.patch(
            f"/api/v1/service-accounts/{account_id}",
            json={"is_active": False},
            headers=auth_headers,
        )

        # List without inactive
        response = await async_client.get(
            "/api/v1/service-accounts",
            headers=auth_headers,
        )
        active_count = response.json()["total"]

        # List with inactive
        response = await async_client.get(
            "/api/v1/service-accounts?include_inactive=true",
            headers=auth_headers,
        )
        all_count = response.json()["total"]

        assert all_count >= active_count

    @pytest.mark.asyncio
    async def test_get_service_account(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test getting a specific service account."""
        # Create an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "Get Test Account", "role": "contributor"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]

        response = await async_client.get(
            f"/api/v1/service-accounts/{account_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == "Get Test Account"
        assert data["role"] == "contributor"

    @pytest.mark.asyncio
    async def test_get_service_account_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test getting a non-existent service account."""
        response = await async_client.get(
            "/api/v1/service-accounts/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_service_account(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test updating a service account."""
        # Create an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "Update Test Account", "role": "reader"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]

        response = await async_client.patch(
            f"/api/v1/service-accounts/{account_id}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
                "role": "admin",
                "rate_limit_per_minute": 200,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["role"] == "admin"
        assert data["rate_limit_per_minute"] == 200

    @pytest.mark.asyncio
    async def test_delete_service_account(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test deleting a service account."""
        # Create an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "Delete Test Account", "role": "reader"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]

        response = await async_client.delete(
            f"/api/v1/service-accounts/{account_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await async_client.get(
            f"/api/v1/service-accounts/{account_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_rotate_api_key(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test rotating a service account's API key."""
        # Create an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "Rotate Key Test Account", "role": "reader"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]
        original_prefix = create_response.json()["api_key_prefix"]

        response = await async_client.post(
            f"/api/v1/service-accounts/{account_id}/rotate-key",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("dsk_")
        # Prefix should be different
        assert data["api_key_prefix"] != original_prefix

    @pytest.mark.asyncio
    async def test_get_usage_stats(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test getting usage statistics."""
        # Create an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "Usage Stats Test Account", "role": "reader"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]

        response = await async_client.get(
            f"/api/v1/service-accounts/{account_id}/usage?days=30",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == account_id
        assert data["period_days"] == 30
        assert "total_requests" in data
        assert "successful_requests" in data
        assert "failed_requests" in data
        assert "operations" in data
        assert "daily_usage" in data


class TestMcpEndpoint:
    """Integration tests for MCP JSON-RPC endpoint."""

    @pytest.mark.asyncio
    async def test_mcp_info(self, async_client: AsyncClient):
        """Test MCP info endpoint."""
        response = await async_client.get("/api/v1/mcp/info")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "DocService MCP Server"
        assert "version" in data
        assert "protocol_version" in data
        assert "tools" in data
        assert "endpoint" in data
        assert "authentication" in data

    @pytest.mark.asyncio
    async def test_mcp_requires_auth(self, async_client: AsyncClient):
        """Test that MCP endpoint requires authentication."""
        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
            },
        )

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_mcp_initialize(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP initialize method."""
        # Create a service account and get API key
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "MCP Test Account", "role": "reader"},
            headers=auth_headers,
        )
        api_key = create_response.json()["api_key"]

        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {},
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["protocolVersion"] is not None
        assert "capabilities" in data["result"]
        assert "serverInfo" in data["result"]

    @pytest.mark.asyncio
    async def test_mcp_tools_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP tools/list method."""
        # Create a service account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "MCP Tools Test Account", "role": "reader"},
            headers=auth_headers,
        )
        api_key = create_response.json()["api_key"]

        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert "result" in data
        assert "tools" in data["result"]

        # Check expected tools are present
        tool_names = [t["name"] for t in data["result"]["tools"]]
        assert "search_documents" in tool_names
        assert "get_document" in tool_names
        assert "list_spaces" in tool_names

    @pytest.mark.asyncio
    async def test_mcp_tools_list_filtered(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP tools/list with restricted operations."""
        # Create a restricted service account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={
                "name": "MCP Restricted Test Account",
                "role": "reader",
                "allowed_operations": ["search_documents"],
            },
            headers=auth_headers,
        )
        api_key = create_response.json()["api_key"]

        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list",
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        tool_names = [t["name"] for t in data["result"]["tools"]]
        assert "search_documents" in tool_names
        assert "get_document" not in tool_names

    @pytest.mark.asyncio
    async def test_mcp_resources_list(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP resources/list method."""
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "MCP Resources Test Account", "role": "reader"},
            headers=auth_headers,
        )
        api_key = create_response.json()["api_key"]

        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "resources/list",
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 4
        assert "result" in data
        assert "resources" in data["result"]

    @pytest.mark.asyncio
    async def test_mcp_unknown_method(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP with unknown method."""
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "MCP Error Test Account", "role": "reader"},
            headers=auth_headers,
        )
        api_key = create_response.json()["api_key"]

        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 5,
                "method": "unknown/method",
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 5
        assert "error" in data
        assert data["error"]["code"] == -32001  # NOT_FOUND

    @pytest.mark.asyncio
    async def test_mcp_rate_limiting(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP rate limiting."""
        # Create an account with very low rate limit
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={
                "name": "MCP Rate Limit Test Account",
                "role": "reader",
                "rate_limit_per_minute": 2,
            },
            headers=auth_headers,
        )
        api_key = create_response.json()["api_key"]

        # Make requests up to the limit
        for _ in range(2):
            response = await async_client.post(
                "/api/v1/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                },
                headers={"Authorization": f"Bearer {api_key}"},
            )
            assert response.status_code == 200

        # Next request should be rate limited
        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_mcp_inactive_account(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test MCP with inactive account."""
        # Create and deactivate an account
        create_response = await async_client.post(
            "/api/v1/service-accounts",
            json={"name": "MCP Inactive Test Account", "role": "reader"},
            headers=auth_headers,
        )
        account_id = create_response.json()["id"]
        api_key = create_response.json()["api_key"]

        # Deactivate the account
        await async_client.patch(
            f"/api/v1/service-accounts/{account_id}",
            json={"is_active": False},
            headers=auth_headers,
        )

        # Try to use the account
        response = await async_client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
            },
            headers={"Authorization": f"Bearer {api_key}"},
        )
        assert response.status_code in [401, 403]
