"""
MCP Client Implementation.
This module provides a client for the MCP (Modular Component Protocol),
which supports multiple transport layers such as stdio, Python, npx, Docker, and HTTP.
"""

import asyncio
import json
import os
import uuid
import time
import contextlib
import sys
from typing import Any, Dict, Optional, List
try:
    # Try unified backend path
    from ..models import MCPServer
    from ..utils.log import get_logger
except ImportError:
    # Fallback for standalone usage
    from models import MCPServer
    # Simple logger fallback
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
else:
    logger = get_logger(__name__)

# Unified MCP Client class for easier usage
class MCPClient:
    """
    A unified MCP client for orchestrator usage.

    This class provides a single entry point for calling tools on various MCP servers.
    It manages multiple MCPClient instances, one for each server, and dynamically
    creates them as needed.
    """

    def __init__(self):
        """
        Initializes the unified MCP client.
        """
        self.clients = {}  # server_name -> MCPClient instance
        self.pool = None

    async def call_tool(self, tool_name: str, parameters: dict = None):
        """
        Calls an MCP tool by its name.

        The tool name should be in the format "server_name.tool_short_name".
        This method will look up the server, create a client for it if one doesn't
        already exist, and then call the tool.

        Note:
            The current implementation includes a mock response for the
            "filesystem" server for testing purposes. The actual client
            initialization and tool calling logic is yet to be implemented.

        Args:
            tool_name (str): The name of the tool to call.
            parameters (dict, optional): The parameters for the tool. Defaults to None.

        Returns:
            A dictionary containing the result of the tool call.
        """
        if parameters is None:
            parameters = {}

        try:
            # Parse tool name to determine server
            # Example: "fs.semantic_search" -> server="filesystem", tool="semantic_search"
            if "." in tool_name:
                server_name, tool_short_name = tool_name.split(".", 1)

                # Get server from registry
                from .registry import get_server
                server = get_server(server_name)

                if not server:
                    return {
                        "success": False,
                        "error": f"Server '{server_name}' not found"
                    }

                # Get or create client for this server
                if server_name not in self.clients:
                    self.clients[server_name] = MCPClientOriginal(server)

                client = self.clients[server_name]

                # For now, return mock result for testing
                # TODO: Implement actual MCP client initialization
                if server_name == "filesystem":
                    if tool_short_name == "semantic_search":
                        return {
                            "success": True,
                            "result": {
                                "results": [
                                    {
                                        "file": f"src/{parameters.get('query', 'test')}_component.tsx",
                                        "score": 0.95,
                                        "snippet": f"// Component related to {parameters.get('query', 'test')}"
                                    }
                                ],
                                "total": 1,
                                "query": parameters.get('query', 'test')
                            },
                            "tool": tool_name,
                            "server": server_name
                        }
                    elif tool_short_name == "pattern_extract":
                        return {
                            "success": True,
                            "result": {
                                "patterns": [
                                    {
                                        "pattern": parameters.get('pattern', 'test'),
                                        "occurrences": 3,
                                        "locations": [
                                            {"line": 15, "column": 10},
                                            {"line": 23, "column": 5}
                                        ]
                                    }
                                ],
                                "file": parameters.get('file_path', 'unknown')
                            },
                            "tool": tool_name,
                            "server": server_name
                        }

                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not implemented yet",
                    "tool": tool_name,
                    "server": server_name
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid tool name format: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

# Keep the original MCPClientInstance class for backward compatibility
class MCPClientInstance:
    """A placeholder for the original MCPClientInstance class for backward compatibility."""
    pass

class BaseTransport:
    """
    A base class for all transport implementations.

    This class defines the interface that all transport classes must implement.
    """
    async def start(self):
        """Starts the transport layer."""
        ...
    async def stop(self):
        """Stops the transport layer."""
        ...
    async def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a payload through the transport layer.

        Args:
            payload (Dict[str, Any]): The payload to send.

        Returns:
            Dict[str, Any]: The response from the server.
        """
        ...

# ---------- STDIO-like process (stdio / python / npx / docker) ----------
class ProcessTransport(BaseTransport):
    """
    A process-based transport for stdio, Python, npx, and Docker.

    This class manages a subprocess and communicates with it over stdin and stdout.

    Usage:
        transport = ProcessTransport(argv=["python", "my_script.py"])
        await transport.start()
        response = await transport.send({"jsonrpc": "2.0", ...})
        await transport.stop()
    """
    
    def __init__(self, argv: List[str], env: Optional[Dict[str, str]] = None, cwd: Optional[str] = None):
        """
        Initializes the process transport.

        Args:
            argv (List[str]): The command and arguments to execute.
            env (Optional[Dict[str, str]], optional): Environment variables for the process. Defaults to None.
            cwd (Optional[str], optional): The working directory for the process. Defaults to None.
        """
        self.argv = argv
        self.env = {**os.environ, **(env or {})}
        self.cwd = cwd
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.pending: Dict[str, asyncio.Future] = {}
        self._listen_task: Optional[asyncio.Task] = None

    async def start(self):
        """Starts the process and sets up communication streams."""
        logger.info(f"Starting process: {' '.join(self.argv)}")
        
        self.proc = await asyncio.create_subprocess_exec(
            *self.argv,
            cwd=self.cwd,
            env=self.env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        
        assert self.proc.stdout and self.proc.stdin
        self.reader, self.writer = self.proc.stdout, self.proc.stdin
        self._listen_task = asyncio.create_task(self._listen())

    async def _listen(self):
        """Listens for responses from the process and fulfills pending futures."""
        assert self.reader
        try:
            while True:
                line = await self.reader.readline()
                if not line:
                    break
                try:
                    msg = json.loads(line.decode("utf-8"))
                    logger.debug(f"Received message: {msg}")
                except Exception as e:
                    logger.warning(f"Invalid JSON from server: {e}")
                    continue
                
                _id = str(msg.get("id"))
                fut = self.pending.pop(_id, None)
                if fut:
                    if "result" in msg:
                        fut.set_result(msg["result"])
                    else:
                        fut.set_exception(RuntimeError(str(msg.get("error"))))
        except Exception as e:
            logger.error(f"Error in process listener: {e}")
        finally:
            logger.info("Process listener stopped")

    async def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a message to the process.

        Args:
            payload (Dict[str, Any]): The payload to send.

        Returns:
            Dict[str, Any]: The response from the server.
        """
        assert self.writer
        _id = str(payload.get("id"))
        if not _id:
            raise RuntimeError("missing id")
        
        fut = asyncio.get_running_loop().create_future()
        self.pending[_id] = fut
        
        try:
            self.writer.write((json.dumps(payload) + "\n").encode("utf-8"))
            await self.writer.drain()
            return await fut
        except Exception as e:
            self.pending.pop(_id, None)
            raise e

    async def stop(self):
        """Stops the process and cleans up resources."""
        logger.info("Stopping process transport")
        
        if self.writer:
            with contextlib.suppress(Exception):
                shutdown_msg = {
                    "jsonrpc": "2.0",
                    "id": str(uuid.uuid4()),
                    "method": "shutdown",
                    "params": {}
                }
                self.writer.write((json.dumps(shutdown_msg) + "\n").encode())
                await self.writer.drain()
                self.writer.close()
                with contextlib.suppress(Exception):
                    await self.writer.wait_closed()
        
        if self._listen_task:
            self._listen_task.cancel()
        
        if self.proc:
            with contextlib.suppress(ProcessLookupError):
                self.proc.kill()
                await self.proc.wait()

# ---------- HTTP/HTTPS ----------
class HTTPTransport(BaseTransport):
    """
    An HTTP/HTTPS transport layer.

    This class uses the `httpx` library to send and receive MCP messages over HTTP.

    Usage:
        transport = HTTPTransport(base_url="http://localhost:8000/mcp")
        await transport.start()
        response = await transport.send({"jsonrpc": "2.0", ...})
        await transport.stop()
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, 
                 bearer_token: Optional[str] = None, verify: bool = True, timeout: float = 60.0):
        """
        Initializes the HTTP transport.

        Args:
            base_url (str): The base URL of the MCP server.
            headers (Optional[Dict[str, str]], optional): Custom headers to include in requests. Defaults to None.
            bearer_token (Optional[str], optional): A bearer token for authentication. Defaults to None.
            verify (bool, optional): Whether to verify the server's TLS certificate. Defaults to True.
            timeout (float, optional): The request timeout in seconds. Defaults to 60.0.
        """
        self.url = base_url.rstrip("/")
        self.headers = headers or {}
        if bearer_token:
            self.headers = {**self.headers, "Authorization": f"Bearer {bearer_token}"}
        self.verify = verify
        self.timeout = timeout
        self.client: Optional[Any] = None

    async def start(self):
        """Initializes the `httpx` client."""
        try:
            import httpx
            self.client = httpx.AsyncClient(
                timeout=self.timeout, 
                verify=self.verify, 
                headers=self.headers
            )
            logger.info(f"HTTP client started for {self.url}")
        except ImportError:
            raise ImportError("httpx is required for HTTP transport")

    async def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends an HTTP POST request to the server.

        Args:
            payload (Dict[str, Any]): The payload to send.

        Returns:
            Dict[str, Any]: The JSON response from the server.
        """
        assert self.client
        try:
            r = await self.client.post(self.url, json=payload)
            r.raise_for_status()
            msg = r.json()
            if "result" in msg:
                return msg["result"]
            raise RuntimeError(str(msg.get("error")))
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            raise

    async def stop(self):
        """Closes the `httpx` client."""
        if self.client:
            await self.client.aclose()
            logger.info("HTTP client stopped")

# ---------- Client ----------
class MCPClientOriginal:
    """
    The original MCP client, which supports multiple transport types.

    This class is responsible for starting, stopping, and communicating with an MCP server
    using the appropriate transport layer based on the server's configuration.
    """
    
    def __init__(self, server: MCPServer):
        """
        Initializes the MCP client.

        Args:
            server (MCPServer): The server to connect to.
        """
        self.server = server
        self.transport: Optional[BaseTransport] = None
        self.initialized = False
        self.start_time = None
        self.error_count = 0
        self.last_error = None

    async def start(self) -> Dict[str, Any]:
        """
        Starts the MCP client with the appropriate transport.

        This method determines the transport type from the server configuration,
        initializes the transport, and then sends an `initialize` RPC to the server.

        Returns:
            Dict[str, Any]: The result of the `initialize` RPC.
        """
        try:
            kind = self.server.kind
            
            if kind == "stdio":
                argv = self.server.cmd or []
                if not argv:
                    raise ValueError("cmd is required for stdio transport")
                self.transport = ProcessTransport(argv, self.server.env, self.server.cwd)
                
            elif kind == "python":
                module = self.server.module
                if not module:
                    raise ValueError("module is required for python transport")
                argv = [sys.executable, "-u", "-m", module] + (self.server.args or [])
                self.transport = ProcessTransport(argv, self.server.env, self.server.cwd)
                
            elif kind == "npx":
                argv = self.server.cmd or ["npx", "-y"]
                if self.server.args:
                    argv += self.server.args
                self.transport = ProcessTransport(argv, self.server.env, self.server.cwd)
                
            elif kind == "docker":
                image = self.server.image
                if not image:
                    raise ValueError("image is required for docker transport")
                
                base = ["docker", "run", "--rm", "-i"]
                for k, v in (self.server.env or {}).items():
                    base += ["-e", f"{k}={v}"]
                if self.server.cwd:
                    base += ["-v", f"{self.server.cwd}:{self.server.cwd}", "-w", self.server.cwd]
                argv = base + [image] + (self.server.entrypoint or []) + (self.server.args or [])
                self.transport = ProcessTransport(argv, None, None)
                
            elif kind == "http":
                url = self.server.url
                if not url:
                    raise ValueError("url is required for http transport")
                self.transport = HTTPTransport(
                    base_url=url,
                    headers=self.server.headers,
                    bearer_token=self.server.bearer_token,
                    verify=self.server.verify_tls if self.server.verify_tls is not None else True,
                    timeout=self.server.timeout_s or 60.0,
                )
            else:
                raise ValueError(f"unsupported transport {kind}")

            # Start transport
            await self.transport.start()
            
            # Initialize MCP server
            init_result = await self._rpc("initialize", {
                "protocolVersion": "2024-05-22",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "chonost-mcp", "version": "0.2.0"},
            })
            
            self.initialized = True
            self.start_time = time.time()
            logger.info(f"MCP server {self.server.name} initialized successfully")
            
            return init_result
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Failed to start MCP server {self.server.name}: {e}")
            raise

    async def _rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Sends an RPC request to the server.

        Args:
            method (str): The name of the RPC method to call.
            params (Optional[Dict[str, Any]], optional): The parameters for the RPC method. Defaults to None.

        Returns:
            Any: The result of the RPC call.
        """
        assert self.transport
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
        if params is not None:
            payload["params"] = params
        return await self.transport.send(payload)

    async def tools_list(self) -> List[Dict[str, Any]]:
        """
        Lists the available tools on the server.

        Returns:
            List[Dict[str, Any]]: A list of available tools.
        """
        try:
            result = await self._rpc("tools/list", {})
            return result.get("tools", [])
        except Exception as e:
            logger.error(f"Failed to list tools from {self.server.name}: {e}")
            return []

    async def tools_call(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Calls a tool on the server.

        Args:
            name (str): The name of the tool to call.
            arguments (Dict[str, Any]): The arguments for the tool.

        Returns:
            Any: The result of the tool call.
        """
        start_time = time.time()
        try:
            result = await self._rpc("tools/call", {
                "name": name, 
                "arguments": arguments
            })
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"Tool {name} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Tool {name} failed after {execution_time:.2f}ms: {e}")
            raise

    async def stop(self) -> None:
        """Stops the client and the transport layer."""
        try:
            if self.transport:
                await self.transport.stop()
                self.transport = None
                self.initialized = False
                logger.info(f"MCP client {self.server.name} stopped")
        except Exception as e:
            logger.error(f"Error stopping MCP client {self.server.name}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Gets the current status of the client.

        Returns:
            Dict[str, Any]: A dictionary containing the client's status.
        """
        uptime = None
        if self.start_time:
            uptime = time.time() - self.start_time
            
        return {
            "name": self.server.name,
            "kind": self.server.kind,
            "status": "running" if self.initialized else "stopped",
            "uptime_seconds": uptime,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "initialized": self.initialized
        }
