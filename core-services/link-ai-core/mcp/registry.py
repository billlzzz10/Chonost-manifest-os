"""
MCP Server Registry.
This module provides a registry for MCP servers, supporting various transport
layers such as stdio, Python, npx, Docker, and HTTP. It includes examples of
16 servers used in a real-world application.
"""

from typing import Dict, Optional
try:
    # Try unified backend path
    from ..models import MCPServer
except ImportError:
    # Fallback for standalone usage
    from models import MCPServer

# Global registry of MCP servers
REGISTRY: Dict[str, MCPServer] = {}

def register_server(server: MCPServer) -> None:
    """
    Registers a new MCP server.

    Args:
        server (MCPServer): The MCP server instance to register.

    Raises:
        ValueError: If a server with the same name is already registered.
    """
    if server.name in REGISTRY:
        raise ValueError(f"Server '{server.name}' already registered")

    REGISTRY[server.name] = server

def unregister_server(name: str) -> None:
    """
    Unregisters an MCP server from the registry.

    Args:
        name (str): The name of the server to unregister.
    """
    if name in REGISTRY:
        del REGISTRY[name]

def get_server(name: str) -> Optional[MCPServer]:
    """
    Gets an MCP server from the registry.

    Args:
        name (str): The name of the server to retrieve.

    Returns:
        Optional[MCPServer]: The MCP server instance, or None if not found.
    """
    return REGISTRY.get(name)

def list_servers() -> Dict[str, MCPServer]:
    """
    Lists all MCP servers in the registry.

    Returns:
        Dict[str, MCPServer]: A dictionary of all registered servers.
    """
    return REGISTRY.copy()

def get_server_names() -> list[str]:
    """
    Gets the names of all registered MCP servers.

    Returns:
        list[str]: A list of server names.
    """
    return list(REGISTRY.keys())

def clear_registry() -> None:
    """Clears the entire server registry."""
    REGISTRY.clear()

# ลงทะเบียน MCP servers เริ่มต้น
def initialize_default_servers():
    """
    Initializes and registers the 16 default MCP servers.

    This function creates instances of `MCPServer` for various services
    and registers them with the server registry.
    """

    # ---------- stdio / python ----------
    filesystem_server = MCPServer(
        name="filesystem",
        kind="python",
        module="backend.mcp.mock_servers.filesystem",  # Mock filesystem server
        env=None,
        cwd=None,
        description="File System MCP Server",
        version="1.0.0"
    )

    postgres_server = MCPServer(
        name="postgres",
        kind="stdio",
        cmd=["mcp-postgres"],                # Binary/script that speaks MCP over stdio
        description="PostgreSQL MCP Server",
        version="1.0.0"
    )

    # ---------- npx (Node) ----------
    github_server = MCPServer(
        name="github",
        kind="npx",
        cmd=["npx", "-y", "mcp-github@latest"],  # Set GH_TOKEN in env
        env={"GH_TOKEN": "YOUR_TOKEN"},
        description="GitHub MCP Server",
        version="1.0.0"
    )

    notion_server = MCPServer(
        name="notion",
        kind="npx",
        cmd=["npx", "-y", "mcp-notion@latest"],
        env={"NOTION_TOKEN": "YOUR_TOKEN"},
        description="Notion MCP Server",
        version="1.0.0"
    )

    slack_server = MCPServer(
        name="slack",
        kind="npx",
        cmd=["npx", "-y", "mcp-slack@latest"],
        env={"SLACK_BOT_TOKEN": "xoxb-..."},
        description="Slack MCP Server",
        version="1.0.0"
    )

    google_drive_server = MCPServer(
        name="google-drive",
        kind="npx",
        cmd=["npx", "-y", "mcp-google-drive@latest"],
        env={"GOOGLE_APPLICATION_CREDENTIALS": "/path/creds.json"},
        description="Google Drive MCP Server",
        version="1.0.0"
    )

    jira_server = MCPServer(
        name="jira",
        kind="npx",
        cmd=["npx", "-y", "mcp-jira@latest"],
        env={
            "JIRA_BASE_URL": "https://your.atlassian.net", 
            "JIRA_TOKEN": "api_token", 
            "JIRA_EMAIL": "you@x"
        },
        description="Jira MCP Server",
        version="1.0.0"
    )

    confluence_server = MCPServer(
        name="confluence",
        kind="npx",
        cmd=["npx", "-y", "mcp-confluence@latest"],
        env={
            "ATLASSIAN_TOKEN": "...", 
            "CONFLUENCE_BASE_URL": "https://..."
        },
        description="Confluence MCP Server",
        version="1.0.0"
    )

    linear_server = MCPServer(
        name="linear",
        kind="npx",
        cmd=["npx", "-y", "mcp-linear@latest"],
        env={"LINEAR_API_KEY": "..."},
        description="Linear MCP Server",
        version="1.0.0"
    )

    airtable_server = MCPServer(
        name="airtable",
        kind="npx",
        cmd=["npx", "-y", "mcp-airtable@latest"],
        env={
            "AIRTABLE_API_KEY": "...", 
            "AIRTABLE_BASE_ID": "..."
        },
        description="Airtable MCP Server",
        version="1.0.0"
    )

    calendar_server = MCPServer(
        name="calendar",
        kind="npx",
        cmd=["npx", "-y", "mcp-google-calendar@latest"],
        env={"GOOGLE_APPLICATION_CREDENTIALS": "/path/creds.json"},
        description="Google Calendar MCP Server",
        version="1.0.0"
    )

    # ---------- Docker ----------
    web_browsing_server = MCPServer(
        name="web-browsing",
        kind="docker",
        image="ghcr.io/yourorg/mcp-browser:latest",
        args=["--headless"],
        env={"PLAYWRIGHT_BROWSERS_PATH": "/ms-playwright"},
        description="Web Browsing MCP Server",
        version="1.0.0"
    )

    pdf_tools_server = MCPServer(
        name="pdf-tools",
        kind="docker",
        image="ghcr.io/yourorg/mcp-pdf:latest",
        description="PDF Tools MCP Server",
        version="1.0.0"
    )

    llm_router_server = MCPServer(
        name="llm-router",
        kind="docker",
        image="ghcr.io/yourorg/mcp-llm-router:latest",
        env={
            "OPENAI_API_KEY": "...", 
            "ANTHROPIC_API_KEY": "..."
        },
        description="LLM Router MCP Server",
        version="1.0.0"
    )

    # ---------- HTTP/HTTPS ----------
    webhook_tools_server = MCPServer(
        name="webhook-tools",
        kind="http",
        url="https://mcp.yourdomain.com/tools",
        headers={"X-Org": "Chonost"},
        bearer_token="YOUR_BEARER_TOKEN",
        verify_tls=True,
        timeout_s=30.0,
        description="Webhook Tools MCP Server",
        version="1.0.0"
    )

    vector_db_server = MCPServer(
        name="vector-db",
        kind="http",
        url="http://localhost:8080/mcp",
        timeout_s=15.0,
        description="Vector Database MCP Server",
        version="1.0.0"
    )

    # Register all servers
    servers = [
        filesystem_server,
        postgres_server,
        github_server,
        notion_server,
        slack_server,
        google_drive_server,
        jira_server,
        confluence_server,
        linear_server,
        airtable_server,
        calendar_server,
        web_browsing_server,
        pdf_tools_server,
        llm_router_server,
        webhook_tools_server,
        vector_db_server
    ]

    for server in servers:
        try:
            register_server(server)
        except Exception as e:
            print(f"Warning: Failed to register server {server.name}: {e}")

# Initialize default servers when module is imported
initialize_default_servers()

# MCP Registry Class for unified interface
class MCPRegistry:
    """
    A class that provides a unified interface to the MCP server registry.
    """

    def __init__(self):
        """Initializes the MCP Registry."""
        pass

    async def list_servers(self):
        """Lists all registered servers."""
        return list_servers()

    async def list_tools(self):
        """
        Lists all available tools from all registered servers.

        Returns:
            list: A list of all available tools.
        """
        servers = list_servers()
        tools = []

        for server_name, server in servers.items():
            # Mock tools for each server type
            if server_name == "filesystem":
                tools.extend([
                    {
                        "name": "fs.semantic_search",
                        "description": "Semantic search in codebase",
                        "category": "filesystem"
                    },
                    {
                        "name": "fs.pattern_extract",
                        "description": "Extract code patterns",
                        "category": "filesystem"
                    }
                ])
            elif server_name == "github":
                tools.extend([
                    {
                        "name": "gh.pr_create_smart",
                        "description": "Create smart pull request",
                        "category": "github"
                    },
                    {
                        "name": "gh.issue_triage",
                        "description": "Triage GitHub issues",
                        "category": "github"
                    }
                ])
            # Add more server-specific tools here

        return tools

    async def get_server(self, name: str):
        """
        Gets a server by its name.

        Args:
            name (str): The name of the server to retrieve.

        Returns:
            The server instance.
        """
        return get_server(name)

    def register_server(self, server):
        """
        Registers a new server.

        Args:
            server: The server instance to register.
        """
        register_server(server)

    def unregister__server(self, name: str):
        """
        Unregisters a server.

        Args:
            name (str): The name of the server to unregister.
        """
        unregister_server(name)
