"""MCP JSON-RPC endpoint.

Sprint C: MCP Integration
"""

from fastapi import APIRouter, Request

from src.api.deps import DbSession
from src.modules.audit.audit_service import AuditService
from src.modules.mcp.auth import McpServiceAccount
from src.modules.mcp.schemas import McpRequest, McpResponse
from src.modules.mcp.server import McpServer

router = APIRouter()


@router.post("", response_model=McpResponse)
async def mcp_endpoint(
    mcp_request: McpRequest,
    request: Request,
    db: DbSession,
    service_account: McpServiceAccount,
) -> McpResponse:
    """MCP JSON-RPC endpoint.

    Authenticate using API key: Authorization: Bearer dsk_...

    This endpoint implements the Model Context Protocol (MCP) for AI agent access.

    **Supported Methods:**
    - `initialize`: Initialize MCP session
    - `tools/list`: List available tools
    - `tools/call`: Execute a tool
    - `resources/list`: List available resources
    - `resources/read`: Read a resource

    **Available Tools:**
    - `search_documents`: Search for documents
    - `get_document`: Get document with full content
    - `get_document_content`: Get document as markdown
    - `list_spaces`: List accessible spaces
    - `get_document_metadata`: Get document metadata
    - `get_document_history`: Get document version history
    """
    client_ip = request.client.host if request.client else None

    # Create MCP server and handle request
    server = McpServer(db, service_account)
    response = await server.handle_request(mcp_request, ip_address=client_ip)

    # Audit log for MCP requests
    audit = AuditService(db)
    await audit.log_event(
        event_type="mcp.request",
        actor_id=service_account.created_by_id,
        actor_email=f"sa:{service_account.name}",
        actor_ip=client_ip,
        resource_type="mcp",
        resource_id=service_account.id,
        resource_name=mcp_request.method,
        details={
            "method": mcp_request.method,
            "has_error": response.error is not None,
        },
    )

    await db.commit()

    return response


@router.get("/info")
async def mcp_info() -> dict:
    """Get MCP server information.

    Returns connection information for setting up MCP clients.
    """
    return {
        "name": "DocService MCP Server",
        "version": "1.0.0",
        "protocol_version": "2024-11-05",
        "description": "Model Context Protocol server for documentation access",
        "endpoint": "/api/v1/mcp",
        "authentication": {
            "type": "bearer",
            "header": "Authorization",
            "format": "Bearer dsk_<api_key>",
        },
        "tools": [
            "search_documents",
            "get_document",
            "get_document_content",
            "list_spaces",
            "get_document_metadata",
            "get_document_history",
        ],
    }
