"""
Unified Pydantic models for the Chonost API Server.
Combines MCP Orchestrator models with database schema models.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid

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

# Database Models (from Prisma schema and SQL migrations)

class NodeType(str, Enum):
    """Node types for the graph system."""
    DOCUMENT = "document"
    CHARACTER = "character"
    CONCEPT = "concept"
    THEME = "theme"
    PLOT_POINT = "plot_point"
    SCENE = "scene"

class EdgeType(str, Enum):
    """Edge types for the graph system."""
    RELATES_TO = "relates_to"
    CONTAINS = "contains"
    INFLUENCES = "influences"
    CONFLICTS_WITH = "conflicts_with"
    SUPPORTS = "supports"
    PRECEDES = "precedes"
    FOLLOWS = "follows"

class User(BaseModel):
    """User model from database schema."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    password_hash: Optional[str] = Field(None, description="Password hash")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserCreate(BaseModel):
    """Request model for creating a user."""
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    """Response model for user data (without password hash)."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class Project(BaseModel):
    """Project model from Prisma schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Document(BaseModel):
    """Document model from Prisma schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Document ID")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    project_id: str = Field(..., description="Project ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Character(BaseModel):
    """Character model from Prisma schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Character ID")
    name: str = Field(..., description="Character name")
    description: Optional[str] = Field(None, description="Character description")
    project_id: str = Field(..., description="Project ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    """Chat session model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Session ID")
    user_id: int = Field(..., description="User ID")
    title: Optional[str] = Field(None, description="Session title")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Message(BaseModel):
    """Message model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    session_id: str = Field(..., description="Session ID")
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(default_factory=datetime.now)

class File(BaseModel):
    """File model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="File ID")
    user_id: int = Field(..., description="User ID")
    original_name: str = Field(..., description="Original filename")
    filename: str = Field(..., description="Stored filename")
    file_path: str = Field(..., description="File path")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    upload_type: str = Field(default="general", description="Upload type")
    processed_data: Optional[Dict[str, Any]] = Field(None, description="Processed data")
    created_at: datetime = Field(default_factory=datetime.now)

class Workflow(BaseModel):
    """Workflow model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Workflow ID")
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    config: Dict[str, Any] = Field(..., description="Workflow configuration")
    is_active: bool = Field(default=True, description="Is workflow active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class WorkflowExecution(BaseModel):
    """Workflow execution model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Execution ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: str = Field(..., description="Execution status")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data")
    error_message: Optional[str] = Field(None, description="Error message")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class Agent(BaseModel):
    """Agent model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Agent ID")
    user_id: int = Field(..., description="User ID")
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    config: Dict[str, Any] = Field(..., description="Agent configuration")
    is_active: bool = Field(default=True, description="Is agent active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AgentExecution(BaseModel):
    """Agent execution model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Execution ID")
    agent_id: str = Field(..., description="Agent ID")
    status: str = Field(..., description="Execution status")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data")
    error_message: Optional[str] = Field(None, description="Error message")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class AgentTemplate(BaseModel):
    """Agent template model from SQL migrations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Template ID")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: Optional[str] = Field(None, description="Template category")
    template_config: Dict[str, Any] = Field(..., description="Template configuration")
    is_public: bool = Field(default=False, description="Is template public")
    created_by: Optional[int] = Field(None, description="Created by user ID")
    usage_count: int = Field(default=0, description="Usage count")
    rating: float = Field(default=0.0, description="Average rating")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Graph System Models (for nodes and edges)

class Node(BaseModel):
    """Node model for the graph system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Node ID")
    title: str = Field(..., description="Node title")
    content: Optional[str] = Field(None, description="Node content")
    type: NodeType = Field(..., description="Node type")
    document_id: Optional[str] = Field(None, description="Associated document ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Node metadata")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "type": self.type.value,
            "document_id": self.document_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Edge(BaseModel):
    """Edge model for the graph system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Edge ID")
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Edge type")
    label: Optional[str] = Field(None, description="Edge label")
    strength: float = Field(default=1.0, description="Edge strength")
    is_explicit: bool = Field(default=True, description="Is edge explicit")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Edge metadata")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "label": self.label,
            "strength": self.strength,
            "is_explicit": self.is_explicit,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
