# How to Set Up MCP Integration

This guide covers creating service accounts and using the platform as both an MCP server (exposing content) and MCP client (consuming external sources).

## Overview

The Model Context Protocol (MCP) integration allows:

- **MCP Server** — Expose your documentation as tools that AI assistants can query
- **MCP Client** — Pull content from external MCP-compatible sources into your docs
- **Service Accounts** — Dedicated API identities for MCP and automation

## Create a Service Account

Service accounts are API identities for machine-to-machine access.

1. Navigate to **Organization Settings** → **Service Accounts**
2. Click **New Service Account**
3. Fill in:
   - **Name**: Descriptive name (e.g., "CI/CD Bot", "MCP Server")
   - **Role**: The role this account has (typically Viewer or Editor)
   - **Clearance Level**: Classification access level (0–3)
4. Click **Create**
5. **Copy the API key** — it is shown only once

**API:**

```
POST /api/v1/service-accounts
{
  "name": "MCP Documentation Server",
  "role": "viewer",
  "clearance_level": 1
}
```

Response:

```json
{
  "id": "sa-uuid",
  "name": "MCP Documentation Server",
  "api_key": "dsa_xxxxxxxxxxxxxxxxxxxxxxxx",
  "role": "viewer",
  "clearance_level": 1
}
```

## Authenticate with a Service Account

Use the API key in the `Authorization` header:

```
Authorization: Bearer dsa_xxxxxxxxxxxxxxxxxxxxxxxx
```

All requests are rate-limited and audited under the service account identity.

## MCP Server (Expose Content)

The platform exposes documentation through MCP tools at `/api/v1/mcp/`.

### Available MCP Tools

| Tool | Description |
|------|------------|
| `search_documents` | Full-text search across accessible documents |
| `get_document` | Retrieve a specific page by ID or slug |
| `list_spaces` | List available spaces and their types |
| `get_document_metadata` | Get page metadata (status, classification, version) |

### MCP Server Configuration

The MCP endpoint is available at:

```
POST /api/v1/mcp/tools/call
{
  "tool": "search_documents",
  "arguments": {
    "query": "approval workflow",
    "limit": 10
  }
}
```

### Connect an AI Assistant

To connect Claude or another MCP-compatible assistant:

1. Create a service account with Viewer role
2. Configure the MCP server URL in your assistant:
   ```json
   {
     "mcpServers": {
       "documentation": {
         "url": "https://your-instance/api/v1/mcp",
         "headers": {
           "Authorization": "Bearer dsa_xxxxxxxxxxxxxxxxxxxxxxxx"
         }
       }
     }
   }
   ```
3. The assistant can now search and retrieve your documentation

## MCP Client (Consume External Sources)

The platform can pull content from external MCP servers:

1. Navigate to **Admin** → **MCP** → **External Sources**
2. Click **Add Source**
3. Configure:
   - **Name**: Descriptive label
   - **URL**: MCP server endpoint
   - **API Key**: Authentication credentials
   - **Sync schedule**: How often to pull content
4. Click **Connect**

Imported content appears as reference material in the editor sidebar.

## Rate Limits

Service accounts have the following default rate limits:

| Tier | Requests per minute | Concurrent requests |
|------|-------------------|-------------------|
| Default | 60 | 5 |
| Premium | 300 | 20 |

Rate limits are configurable per service account by organization admins.

## Monitoring Usage

View service account activity:

```
GET /api/v1/service-accounts/{sa_id}/usage?period=30d
```

This returns request counts, error rates, and the most-accessed resources.

All service account actions appear in the [audit trail](../reference/api/audit.md) with the service account as the actor.
