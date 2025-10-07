# API Documentation

This document describes the currently implemented endpoints for the Chonost Manuscript OS API server (`services/api-server`). The service focuses on the MCP orchestrator flow; additional endpoints listed in earlier drafts have not been implemented yet.

## Base URL

- Local development: `http://localhost:8000`

## Authentication

- Public endpoints (`/health`, `/mcp/*`) do not require authentication.
- The `/api/rag` endpoint uses JWT bearer tokens. Supply a token signed with the `JWT_SECRET` environment variable (defaults to `your-secret-key-change-in-production`).

## Endpoints

### Health

```
GET /health
```

Returns a simple JSON payload describing service status.

**Response**

```json
{
  "status": "healthy",
  "service": "mcp-orchestrator",
  "version": "2.2.0"
}
```

### List MCP Servers

```
GET /mcp/servers
```

Lists available MCP servers registered with the orchestrator. Returns `503` when the registry is not initialised.

### List MCP Tools

```
GET /mcp/tools
```

Lists tools exposed by the MCP registry. Returns `503` when the registry is not initialised.

### Orchestrator Status

```
GET /mcp/status
```

Returns component availability information (`registry`, `client`, and `settings`). Helpful for debugging missing dependencies.

### Call MCP Tool

```
POST /mcp/call
```

Executes a tool via the MCP client.

**Request body**

```json
{
  "tool": "filesystem.list",
  "parameters": {}
}
```

Returns the tool invocation result or an error when the client is not available.

### Retrieval Stub

```
POST /api/rag
```

Placeholder endpoint for future RAG functionality. Requires a valid JWT. The current implementation echoes the query and user id.

**Request body**

```json
{
  "query": "Explain the orchestrator pipeline"
}
```

**Response**

```json
{
  "success": true,
  "data": "RAG/Notion response for query: Explain the orchestrator pipeline (User: user-id)",
  "user_id": "user-id"
}
```

## Error Handling

The API returns RFC 7807-style JSON responses via FastAPI. Common failure paths include:

- `400` when `/mcp/call` is invoked without a `tool` field.
- `401` when `/api/rag` is called with an invalid JWT.
- `503` when MCP dependencies are not initialised.

## Future Work

- Expand `/api` routes beyond the JWT-protected RAG stub.
- Finish wiring MCP registry/client initialisation in production environments.
- Align documentation with upcoming schema or orchestration changes.
