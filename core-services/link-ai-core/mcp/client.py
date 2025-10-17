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

from models import MCPServer
from utils.log import get_logger

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
        """
        if parameters is None:
            parameters = {}

        try:
            if "." not in tool_name:
                return {
                    "success": False,
                    "error": f"Invalid tool name format: {tool_name}"
                }

            server_name, tool_short_name = tool_name.split(".", 1)

            # Get server from registry
            from mcp.registry import get_server
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

            # Call the tool on the specific client
            result = await client.tools_call(tool_short_name, parameters)
            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "server": server_name
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
        ...
    async def stop(self):
        ...
    async def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

class ProcessTransport(BaseTransport):
    """
    A process-based transport for stdio, Python, npx, and Docker.
    """
    
    def __init__(self, argv: List[str], env: Optional[Dict[str, str]] = None, cwd: Optional[str] = None):
        self.argv = argv
        self.env = {**os.environ, **(env or {})}
        self.cwd = cwd
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.pending: Dict[str, asyncio.Future] = {}
        self._listen_task: Optional[asyncio.Task] = None

    async def start(self):
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
        assert self.reader
        try:
            while True:
                line = await self.reader.readline()
                if not line: break
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
        assert self.writer
        _id = str(payload.get("id"))
        if not _id: raise RuntimeError("missing id")
        
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
        logger.info("Stopping process transport")
        if self.writer:
            with contextlib.suppress(Exception):
                shutdown_msg = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "shutdown", "params": {}}
                self.writer.write((json.dumps(shutdown_msg) + "\n").encode())
                await self.writer.drain()
                self.writer.close()
                await self.writer.wait_closed()
        if self._listen_task: self._listen_task.cancel()
        if self.proc:
            with contextlib.suppress(ProcessLookupError):
                self.proc.kill()
                await self.proc.wait()

class HTTPTransport(BaseTransport):
    """
    An HTTP/HTTPS transport layer.
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, 
                 bearer_token: Optional[str] = None, verify: bool = True, timeout: float = 60.0):
        self.url = base_url.rstrip("/")
        self.headers = headers or {}
        if bearer_token: self.headers["Authorization"] = f"Bearer {bearer_token}"
        self.verify = verify
        self.timeout = timeout
        self.client: Optional[Any] = None

    async def start(self):
        try:
            import httpx
            self.client = httpx.AsyncClient(timeout=self.timeout, verify=self.verify, headers=self.headers)
            logger.info(f"HTTP client started for {self.url}")
        except ImportError:
            raise ImportError("httpx is required for HTTP transport")

    async def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        assert self.client
        try:
            r = await self.client.post(self.url, json=payload)
            r.raise_for_status()
            msg = r.json()
            if "result" in msg: return msg["result"]
            raise RuntimeError(str(msg.get("error")))
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            raise

    async def stop(self):
        if self.client:
            await self.client.aclose()
            logger.info("HTTP client stopped")

class MCPClientOriginal:
    """
    The original MCP client, which supports multiple transport types.
    """
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.transport: Optional[BaseTransport] = None
        self.initialized = False
        self.start_time = None
        self.error_count = 0
        self.last_error = None

    async def start(self) -> Dict[str, Any]:
        try:
            kind = self.server.kind
            if kind == "stdio":
                if not self.server.cmd: raise ValueError("cmd is required for stdio transport")
                self.transport = ProcessTransport(self.server.cmd, self.server.env, self.server.cwd)
            elif kind == "python":
                if not self.server.module: raise ValueError("module is required for python transport")
                argv = [sys.executable, "-u", "-m", self.server.module] + (self.server.args or [])
                self.transport = ProcessTransport(argv, self.server.env, self.server.cwd)
            elif kind == "npx":
                argv = self.server.cmd or ["npx", "-y"]
                if self.server.args: argv += self.server.args
                self.transport = ProcessTransport(argv, self.server.env, self.server.cwd)
            elif kind == "docker":
                if not self.server.image: raise ValueError("image is required for docker transport")
                base = ["docker", "run", "--rm", "-i"]
                for k, v in (self.server.env or {}).items(): base += ["-e", f"{k}={v}"]
                if self.server.cwd: base += ["-v", f"{self.server.cwd}:{self.server.cwd}", "-w", self.server.cwd]
                argv = base + [self.server.image] + (self.server.entrypoint or []) + (self.server.args or [])
                self.transport = ProcessTransport(argv, None, None)
            elif kind == "http":
                if not self.server.url: raise ValueError("url is required for http transport")
                self.transport = HTTPTransport(
                    base_url=self.server.url, headers=self.server.headers, bearer_token=self.server.bearer_token,
                    verify=self.server.verify_tls if self.server.verify_tls is not None else True,
                    timeout=self.server.timeout_s or 60.0,
                )
            else:
                raise ValueError(f"unsupported transport {kind}")

            await self.transport.start()
            init_result = await self._rpc("initialize", {
                "protocolVersion": "2024-05-22", "capabilities": {"tools": {}},
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
        assert self.transport
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
        if params is not None: payload["params"] = params
        return await self.transport.send(payload)

    async def tools_list(self) -> List[Dict[str, Any]]:
        try:
            result = await self._rpc("tools/list", {})
            return result.get("tools", [])
        except Exception as e:
            logger.error(f"Failed to list tools from {self.server.name}: {e}")
            return []

    async def tools_call(self, name: str, arguments: Dict[str, Any]) -> Any:
        start_time = time.time()
        try:
            result = await self._rpc("tools/call", {"name": name, "arguments": arguments})
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"Tool {name} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Tool {name} failed after {execution_time:.2f}ms: {e}")
            raise

    async def stop(self) -> None:
        try:
            if self.transport:
                await self.transport.stop()
                self.transport = None
                self.initialized = False
                logger.info(f"MCP client {self.server.name} stopped")
        except Exception as e:
            logger.error(f"Error stopping MCP client {self.server.name}: {e}")

    def get_status(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time if self.start_time else None
        return {
            "name": self.server.name, "kind": self.server.kind,
            "status": "running" if self.initialized else "stopped",
            "uptime_seconds": uptime, "error_count": self.error_count,
            "last_error": self.last_error, "initialized": self.initialized
        }