"""MCP JSON-RPC server implementation.

Sprint C: MCP Integration

Implements the Model Context Protocol (MCP) server for AI agent access.
Follows the MCP specification for JSON-RPC communication.
"""

import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.service_account import ServiceAccount
from src.modules.mcp.schemas import (
    GetDocumentParams,
    ListSpacesParams,
    McpError,
    McpRequest,
    McpResponse,
    SearchDocumentsParams,
)
from src.modules.mcp.service import ServiceAccountService
from src.modules.mcp.tools import McpTools


# MCP Error Codes (JSON-RPC standard + custom)
class McpErrorCode:
    """MCP/JSON-RPC error codes."""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Custom codes
    PERMISSION_DENIED = -32000
    NOT_FOUND = -32001
    RATE_LIMITED = -32002


# Tool definitions for MCP discovery
MCP_TOOLS = [
    {
        "name": "search_documents",
        "description": "Search for documents in the documentation platform",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query text",
                },
                "space_id": {
                    "type": "string",
                    "description": "Optional space UUID to filter results",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "maximum": 100,
                    "description": "Maximum number of results",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_document",
        "description": "Get a document by ID with full content in markdown format",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document UUID",
                },
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "get_document_content",
        "description": "Get document content as plain markdown text",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document UUID",
                },
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "list_spaces",
        "description": "List accessible documentation spaces",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {
                    "type": "string",
                    "description": "Optional workspace UUID to filter",
                },
            },
        },
    },
    {
        "name": "get_document_metadata",
        "description": "Get document metadata (status, version, dates, owner)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document UUID",
                },
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "get_document_history",
        "description": "Get document version history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document UUID",
                },
            },
            "required": ["document_id"],
        },
    },
]

# Resource templates for MCP discovery
MCP_RESOURCES = [
    {
        "uriTemplate": "doc://{org}/{workspace}/{space}/{page}",
        "name": "Document",
        "description": "Access a specific document by path",
    },
    {
        "uriTemplate": "space://{org}/{workspace}/{space}",
        "name": "Space",
        "description": "Access a documentation space",
    },
]


class McpServer:
    """MCP JSON-RPC server.

    Handles MCP protocol requests and dispatches to appropriate tools.
    All operations are logged for audit and usage tracking.
    """

    def __init__(
        self,
        db: AsyncSession,
        service_account: ServiceAccount,
    ):
        self.db = db
        self.service_account = service_account
        self.tools = McpTools(db, service_account)
        self.service = ServiceAccountService(db)

    async def handle_request(
        self, request: McpRequest, ip_address: str | None = None
    ) -> McpResponse:
        """Handle an MCP JSON-RPC request.

        Args:
            request: The MCP request
            ip_address: Client IP address for logging

        Returns:
            MCP response with result or error
        """
        start_time = time.time()
        response_code = 200
        error_message = None
        resource_id = None

        try:
            result = await self._dispatch(request)
            return McpResponse(
                id=request.id,
                result=result,
            )
        except PermissionError as e:
            response_code = 403
            error_message = str(e)
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.PERMISSION_DENIED,
                    message=str(e),
                ).model_dump(),
            )
        except ValueError as e:
            response_code = 404
            error_message = str(e)
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.NOT_FOUND,
                    message=str(e),
                ).model_dump(),
            )
        except KeyError as e:
            response_code = 400
            error_message = f"Missing parameter: {e}"
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.INVALID_PARAMS,
                    message=error_message,
                ).model_dump(),
            )
        except Exception as e:
            response_code = 500
            error_message = str(e)
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.INTERNAL_ERROR,
                    message="Internal server error",
                ).model_dump(),
            )
        finally:
            # Record usage
            elapsed_ms = int((time.time() - start_time) * 1000)
            await self.service.record_usage(
                account_id=self.service_account.id,
                operation=request.method,
                response_code=response_code,
                ip_address=ip_address,
                resource_id=resource_id,
                response_time_ms=elapsed_ms,
                error_message=error_message,
            )

    async def _dispatch(self, request: McpRequest) -> dict[str, Any]:
        """Dispatch request to appropriate handler.

        Args:
            request: The MCP request

        Returns:
            Result dictionary
        """
        method = request.method
        params = request.params or {}

        # MCP protocol methods
        if method == "initialize":
            return self._handle_initialize(params)
        elif method == "tools/list":
            return self._handle_tools_list()
        elif method == "resources/list":
            return self._handle_resources_list()
        elif method == "tools/call":
            return await self._handle_tools_call(params)
        elif method == "resources/read":
            return await self._handle_resources_read(params)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _handle_initialize(self, params: dict) -> dict:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
            },
            "serverInfo": {
                "name": "DocService MCP Server",
                "version": "1.0.0",
            },
        }

    def _handle_tools_list(self) -> dict:
        """Handle tools/list request."""
        # Filter tools based on allowed operations
        allowed_ops = self.service_account.allowed_operations
        if allowed_ops:
            tools = [t for t in MCP_TOOLS if t["name"] in allowed_ops]
        else:
            tools = MCP_TOOLS

        return {"tools": tools}

    def _handle_resources_list(self) -> dict:
        """Handle resources/list request."""
        return {"resources": MCP_RESOURCES}

    async def _handle_tools_call(self, params: dict) -> dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "search_documents":
            search_params = SearchDocumentsParams(**tool_args)
            results = await self.tools.search_documents(search_params)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str([r.model_dump() for r in results]),
                    }
                ]
            }

        elif tool_name == "get_document":
            doc_params = GetDocumentParams(document_id=tool_args["document_id"])
            doc = await self.tools.get_document(doc_params)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": doc.model_dump_json(),
                    }
                ]
            }

        elif tool_name == "get_document_content":
            doc_params = GetDocumentParams(document_id=tool_args["document_id"])
            content = await self.tools.get_document_content(doc_params)
            return {"content": [{"type": "text", "text": content}]}

        elif tool_name == "list_spaces":
            list_params = ListSpacesParams(**tool_args)
            spaces = await self.tools.list_spaces(list_params)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str([s.model_dump() for s in spaces]),
                    }
                ]
            }

        elif tool_name == "get_document_metadata":
            doc_params = GetDocumentParams(document_id=tool_args["document_id"])
            metadata = await self.tools.get_document_metadata(doc_params)
            return {"content": [{"type": "text", "text": str(metadata)}]}

        elif tool_name == "get_document_history":
            doc_params = GetDocumentParams(document_id=tool_args["document_id"])
            history = await self.tools.get_document_history(doc_params)
            return {"content": [{"type": "text", "text": str(history)}]}

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _handle_resources_read(self, params: dict) -> dict:
        """Handle resources/read request."""
        uri = params.get("uri", "")

        if uri.startswith("doc://"):
            # Parse doc://org/workspace/space/page
            parts = uri[6:].split("/")
            if len(parts) < 4:
                raise ValueError("Invalid document URI format")
            page_id = parts[-1]
            doc_params = GetDocumentParams(document_id=page_id)
            content = await self.tools.get_document_content(doc_params)
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": content,
                    }
                ]
            }

        raise ValueError(f"Unknown resource URI: {uri}")
