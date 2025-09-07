#!/usr/bin/env python3
"""
Mock Filesystem MCP Server for testing
Implements basic MCP protocol for filesystem operations
"""

import asyncio
import json
import sys
import os

class MockFilesystemServer:
    """Mock MCP server for filesystem operations"""

    def __init__(self):
        self.tools = [
            {
                "name": "semantic_search",
                "description": "Search for files using semantic similarity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "pattern_extract",
                "description": "Extract code patterns from files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Pattern to extract"},
                        "file_path": {"type": "string", "description": "File path to analyze"}
                    },
                    "required": ["pattern"]
                }
            }
        ]

    async def handle_message(self, message):
        """Handle incoming MCP messages"""
        try:
            method = message.get("method")
            params = message.get("params", {})

            if method == "initialize":
                return {
                    "protocolVersion": "2024-05-22",
                    "capabilities": {
                        "tools": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "mock-filesystem-server",
                        "version": "1.0.0"
                    }
                }

            elif method == "tools/list":
                return {"tools": self.tools}

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "semantic_search":
                    query = arguments.get("query", "")
                    limit = arguments.get("limit", 10)
                    return self._mock_semantic_search(query, limit)

                elif tool_name == "pattern_extract":
                    pattern = arguments.get("pattern", "")
                    file_path = arguments.get("file_path", "")
                    return self._mock_pattern_extract(pattern, file_path)

                else:
                    return {"error": f"Unknown tool: {tool_name}"}

            else:
                return {"error": f"Unknown method: {method}"}

        except Exception as e:
            return {"error": str(e)}

    def _mock_semantic_search(self, query, limit):
        """Mock semantic search implementation"""
        # Return mock results
        mock_results = [
            {
                "file": f"src/{query}_component.tsx",
                "score": 0.95,
                "snippet": f"// Component related to {query}"
            },
            {
                "file": f"tests/{query}_test.py",
                "score": 0.87,
                "snippet": f"def test_{query}():"
            }
        ][:limit]

        return {
            "results": mock_results,
            "total": len(mock_results),
            "query": query
        }

    def _mock_pattern_extract(self, pattern, file_path):
        """Mock pattern extraction implementation"""
        return {
            "patterns": [
                {
                    "pattern": pattern,
                    "occurrences": 3,
                    "locations": [
                        {"line": 15, "column": 10},
                        {"line": 23, "column": 5},
                        {"line": 45, "column": 12}
                    ]
                }
            ],
            "file": file_path or "unknown"
        }


async def main():
    """Main entry point for the mock server"""
    server = MockFilesystemServer()

    # Simple stdin/stdout MCP server
    print("Mock Filesystem MCP Server started", file=sys.stderr)

    try:
        for line in sys.stdin:
            try:
                message = json.loads(line.strip())
                response = await server.handle_message(message)

                # Add jsonrpc version and id
                response["jsonrpc"] = "2.0"
                response["id"] = message.get("id")

                print(json.dumps(response))

            except json.JSONDecodeError:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }))
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": str(e)},
                    "id": message.get("id")
                }))

    except KeyboardInterrupt:
        print("Mock Filesystem MCP Server stopped", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
