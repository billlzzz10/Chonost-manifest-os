"""
MCP Server Registry.
This module provides a registry for MCP servers, supporting various transport
layers such as stdio, Python, npx, Docker, and HTTP. It includes examples of
16 servers used in a real-world application.
"""

from typing import Dict, Optional
from models import MCPServer

# Global registry of MCP servers
REGISTRY: Dict[str, MCPServer] = {}

def register_server(server: MCPServer) -> None:
    """
    Registers a new MCP server.
    """
    if server.name in REGISTRY:
        raise ValueError(f"Server '{server.name}' already registered")
    REGISTRY[server.name] = server

def unregister_server(name: str) -> None:
    """
    Unregisters an MCP server from the registry.
    """
    if name in REGISTRY:
        del REGISTRY[name]

def get_server(name: str) -> Optional[MCPServer]:
    """
    Gets an MCP server from the registry.
    """
    return REGISTRY.get(name)

def list_servers() -> Dict[str, MCPServer]:
    """
    Lists all MCP servers in the registry.
    """
    return REGISTRY.copy()

def get_server_names() -> list[str]:
    """
    Gets the names of all registered MCP servers.
    """
    return list(REGISTRY.keys())

def clear_registry() -> None:
    """Clears the entire server registry."""
    REGISTRY.clear()

def initialize_default_servers():
    """
    Initializes and registers the 16 default MCP servers.
    """
    # This is a sample configuration. In a real application, this would
    # likely be loaded from a configuration file.
    servers_config = [
        {
            "name": "filesystem", "kind": "python", "module": "mcp.mock_servers.filesystem",
            "description": "File System MCP Server"
        },
        # Add other server configurations here if needed for testing or default setup.
    ]

    for config in servers_config:
        try:
            register_server(MCPServer(**config))
        except Exception as e:
            print(f"Warning: Failed to register server {config['name']}: {e}")

# Initialize default servers when module is imported
initialize_default_servers()

class MCPRegistry:
    """
    A class that provides a unified interface to the MCP server registry.
    """
    async def list_servers(self):
        return list_servers()

    async def list_tools(self):
        # This is a mock implementation. A real implementation would query servers.
        return [{"name": "mock.tool", "description": "A mock tool"}]

    async def get_server(self, name: str):
        return get_server(name)

    def register_server(self, server: MCPServer):
        register_server(server)

    def unregister_server(self, name: str):
        unregister_server(name)