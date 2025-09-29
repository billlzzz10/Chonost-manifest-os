#!/usr/bin/env python3
"""
Mock Filesystem MCP Server for Testing.
This module implements a mock MCP (Modular Component Protocol) server for
filesystem operations, designed for testing purposes. It simulates the behavior
of a real filesystem MCP server by implementing the basic MCP protocol.
"""

import asyncio
import json
import sys
import os

class MockFilesystemServer:
    """
    A mock MCP server for filesystem operations.

    This class simulates the behavior of a real filesystem MCP server by providing
    mock implementations for various tool calls such as semantic search and pattern extraction.
    """

    def __init__(self):
        """Initializes the mock filesystem server."""
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
        """
        Handles incoming MCP messages.

        This method parses the incoming message, determines the requested method,
        and calls the appropriate handler.

        Args:
            message (dict): The incoming MCP message.

        Returns:
            dict: The response to the MCP message.
        """
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
        """
        A mock implementation of the semantic search tool.

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return.

        Returns:
            dict: A dictionary of mock search results.
        """
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
        """
        A mock implementation of the pattern extraction tool.

        Args:
            pattern (str): The pattern to extract.
            file_path (str): The path to the file to analyze.

        Returns:
            dict: A dictionary of mock pattern extraction results.
        """
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
    """
    The main entry point for the mock server.

    This function creates an instance of the `MockFilesystemServer` and listens
    for incoming messages on stdin. It then processes the messages and prints
    the responses to stdout.
    """
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
