"""
Pydantic models for the MCP Orchestrator.
This module supports multiple transport types: stdio, python, npx, docker, and http.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

TransportKind = Literal["stdio", "python", "npx", "docker", "http"]

class MCPServer(BaseModel):
    """
    An MCP Server configuration that supports multiple transport types.

    Attributes:
        name (str): The server name/identifier.
        kind (TransportKind): The transport type.
        env (Optional[Dict[str, str]]): Environment variables for the server.
        cwd (Optional[str]): The working directory for the server.
        description (Optional[str]): A description of the server.
        version (Optional[str]): The server version.
        cmd (Optional[List[str]]): Command line arguments for stdio/npx/docker.
        module (Optional[str]): The Python module for `python -m <module>`.
        image (Optional[str]): The Docker image name.
        entrypoint (Optional[List[str]]): A Docker entrypoint override.
        args (Optional[List[str]]): Extra arguments for the process/docker.
        url (Optional[str]): The HTTP/HTTPS endpoint URL.
        headers (Optional[Dict[str, str]]): HTTP headers.
        bearer_token (Optional[str]): A bearer token for authentication.
        verify_tls (Optional[bool]): A flag indicating whether to verify the
                                      TLS certificate.
        timeout_s (Optional[float]): The request timeout in seconds.
    """
    
    name: str = Field(..., description="Server name/identifier")
    kind: TransportKind = Field(..., description="Transport type")
    
    # Shared configuration
    env: Optional[Dict[str, str]] = Field(
        default=None,
        description="Environment variables for the server"
    )
    cwd: Optional[str] = Field(
        default=None,
        description="Working directory for the server"
    )
    description: Optional[str] = Field(
        default=None,
        description="Server description"
    )
    version: Optional[str] = Field(
        default="1.0.0",
        description="Server version"
    )

    # stdio | python | npx | docker
    cmd: Optional[List[str]] = Field(
        default=None,
        description="Command line arguments for stdio/npx/docker"
    )
    module: Optional[str] = Field(
        default=None,
        description="Python module for python -m <module>"
    )
    image: Optional[str] = Field(
        default=None,
        description="Docker image name"
    )
    entrypoint: Optional[List[str]] = Field(
        default=None,
        description="Docker entrypoint override"
    )
    args: Optional[List[str]] = Field(
        default=None,
        description="Extra arguments for process/docker"
    )

    # http(s)
    url: Optional[str] = Field(
        default=None,
        description="HTTP/HTTPS endpoint URL"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="HTTP headers"
    )
    bearer_token: Optional[str] = Field(
        default=None,
        description="Bearer token for authentication"
    )
    verify_tls: Optional[bool] = Field(
        default=True,
        description="Verify TLS certificate"
    )
    timeout_s: Optional[float] = Field(
        default=60.0,
        description="Request timeout in seconds"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Server name cannot be empty')
        return v.strip()

    @validator('cmd')
    def validate_cmd(cls, v):
        if v is not None and (not v or len(v) == 0):
            raise ValueError('Command cannot be empty')
        return v

    @validator('url')
    def validate_url(cls, v, values):
        if values.get('kind') == 'http' and not v:
            raise ValueError('URL is required for HTTP transport')
        return v

    @validator('module')
    def validate_module(cls, v, values):
        if values.get('kind') == 'python' and not v:
            raise ValueError('Module is required for Python transport')
        return v

    @validator('image')
    def validate_image(cls, v, values):
        if values.get('kind') == 'docker' and not v:
            raise ValueError('Image is required for Docker transport')
        return v

class MCPTool(BaseModel):
    """
    An MCP Tool definition.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool.
        inputSchema (Optional[Dict[str, Any]]): A JSON schema for the tool's
                                                 input.
    """

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON Schema for tool input"
    )

class MCPListToolsReq(BaseModel):
    """
    A request to list tools from an MCP server.

    Attributes:
        server (str): The name of the server to query.
    """

    server: str = Field(..., description="Server name to query")

class MCPListToolsResp(BaseModel):
    """
    A response containing tools from an MCP server.

    Attributes:
        tools (List[MCPTool]): A list of available tools.
        server (str): The name of the server.
        timestamp (datetime): The timestamp of the response.
    """

    tools: List[MCPTool] = Field(..., description="List of available tools")
    server: str = Field(..., description="Server name")
    timestamp: datetime = Field(default_factory=datetime.now)

class MCPCallReq(BaseModel):
    """
    A request to call a tool on an MCP server.

    Attributes:
        server (str): The name of the server.
        tool (str): The name of the tool to call.
        arguments (Dict[str, Any]): The arguments for the tool.
    """

    server: str = Field(..., description="Server name")
    tool: str = Field(..., description="Tool name to call")
    arguments: Dict[str, Any] = Field(
        default={},
        description="Tool arguments"
    )

class MCPCallResp(BaseModel):
    """
    A response from a tool call.

    Attributes:
        result (Any): The result of the tool execution.
        server (str): The name of the server.
        tool (str): The name of the tool.
        timestamp (datetime): The timestamp of the response.
        execution_time_ms (Optional[float]): The execution time of the tool in
                                             milliseconds.
    """

    result: Any = Field(..., description="Tool execution result")
    server: str = Field(..., description="Server name")
    tool: str = Field(..., description="Tool name")
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = Field(
        default=None,
        description="Tool execution time in milliseconds"
    )

class MCPServersResp(BaseModel):
    """
    A response containing the available MCP servers.

    Attributes:
        servers (List[str]): A list of server names.
    """

    servers: List[str] = Field(..., description="List of server names")

class MCPError(BaseModel):
    """
    An MCP Error response.

    Attributes:
        code (int): The error code.
        message (str): The error message.
        details (Optional[Dict[str, Any]]): Additional error details.
        timestamp (datetime): The timestamp of the error.
    """

    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheck(BaseModel):
    """
    A health check response.

    Attributes:
        status (str): The status of the service.
        timestamp (datetime): The timestamp of the health check.
        version (str): The version of the service.
        uptime_seconds (Optional[float]): The uptime of the service in seconds.
        mcp_servers (List[str]): A list of available MCP servers.
    """

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="Service version")
    uptime_seconds: Optional[float] = Field(
        default=None,
        description="Service uptime in seconds"
    )
    mcp_servers: List[str] = Field(
        default=[],
        description="Available MCP servers"
    )

class ServerStatus(BaseModel):
    """
    The status of an MCP Server.

    Attributes:
        name (str): The name of the server.
        status (str): The status of the server (running, stopped, error).
        uptime_seconds (Optional[float]): The uptime of the server in seconds.
        last_used (Optional[datetime]): The last time the server was used.
        error_count (int): The number of errors encountered.
        last_error (Optional[str]): The last error message.
    """

    name: str = Field(..., description="Server name")
    status: str = Field(..., description="Server status (running, stopped, error)")
    uptime_seconds: Optional[float] = Field(
        default=None,
        description="Server uptime in seconds"
    )
    last_used: Optional[datetime] = Field(
        default=None,
        description="Last time server was used"
    )
    error_count: int = Field(
        default=0,
        description="Number of errors encountered"
    )
    last_error: Optional[str] = Field(
        default=None,
        description="Last error message"
    )
