# mcp-server/main.py
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Union
import json
import asyncio
import os
import aiofiles
from pathlib import Path
import yaml

# Define the root directory for all user file operations
ROOT_DIR = Path("/app/root")  # <-- Adjust as appropriate for your deployment!

app = FastAPI(title="Model Context Protocol Server", version="2.0.0")

class MCPRequest(BaseModel):
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class MCPResource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPServer:
    # Define root directory for allowed file access
    ALLOWED_FILES_ROOT = Path("allowed_files").resolve()  # Adjust path to desired root directory
    
    def __init__(self):
        self.resources: Dict[str, MCPResource] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.load_mcp_config()
        self.setup_default_resources()
        self.setup_default_tools()
    
    def load_mcp_config(self):
        try:
            with open('config/mcp_tools.yaml', 'r') as f:
                self.mcp_config = yaml.safe_load(f)
        except FileNotFoundError:
            self.mcp_config = {"resources": [], "tools": []}
    
    def setup_default_resources(self):
        """Setup default file and folder resources"""
        # File system resources
        self.resources["filesystem"] = MCPResource(
            uri="file://",
            name="File System",
            description="Access to local file system",
            mimeType="application/octet-stream"
        )
        
        # Codebase resource
        self.resources["codebase"] = MCPResource(
            uri="codebase://",
            name="Codebase",
            description="Project codebase with intelligent parsing",
            mimeType="text/plain"
        )
        
        # Document resource
        self.resources["documents"] = MCPResource(
            uri="documents://",
            name="Documents",
            description="Document collection with semantic search",
            mimeType="text/plain"
        )
    
    def setup_default_tools(self):
        """Setup default MCP tools"""
        # File operations
        self.tools["read_file"] = MCPTool(
            name="read_file",
            description="Read content from a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path"]
            }
        )
        
        self.tools["write_file"] = MCPTool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["path", "content"]
            }
        )
        
        self.tools["list_directory"] = MCPTool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                    "recursive": {"type": "boolean", "default": False}
                },
                "required": ["path"]
            }
        )
        
        # Codebase tools
        self.tools["analyze_code"] = MCPTool(
            name="analyze_code",
            description="Analyze code structure and dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Code file or directory path"},
                    "language": {"type": "string", "description": "Programming language"}
                },
                "required": ["path"]
            }
        )
        
        # Document tools
        self.tools["search_documents"] = MCPTool(
            name="search_documents",
            description="Search through document collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        )
    
    async def handle_request(self, request: MCPRequest) -> Dict[str, Any]:
        """Handle MCP request"""
        method = request.method
        params = request.params
        
        try:
            if method == "resources/list":
                return await self.list_resources()
            elif method == "resources/read":
                return await self.read_resource(params.get("uri"))
            elif method == "tools/list":
                return await self.list_tools()
            elif method == "tools/call":
                return await self.call_tool(params.get("name"), params.get("arguments", {}))
            else:
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources"""
        return {
            "resources": [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                }
                for resource in self.resources.values()
            ]
        }
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read resource content"""
        if uri.startswith("file://"):
            path = uri[7:]  # Remove file:// prefix
            return await self.read_file_resource(path)
        elif uri.startswith("codebase://"):
            path = uri[11:]  # Remove codebase:// prefix
            return await self.read_codebase_resource(path)
        elif uri.startswith("documents://"):
            path = uri[12:]  # Remove documents:// prefix
            return await self.read_document_resource(path)
        else:
            return {"error": f"Unknown resource URI scheme: {uri}"}
    
    async def read_file_resource(self, path: str) -> Dict[str, Any]:
        """Read file system resource"""
        try:
            full_path = Path(path)
            if not full_path.exists():
                return {"error": f"File not found: {path}"}
            if full_path.is_file():
                async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                return {
                    "contents": [{
                        "uri": f"file://{path}",
                        "mimeType": "text/plain",
                        "text": content
                    }]
                }
            else:
                # Directory listing
                items = []
                for item in full_path.iterdir():
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "uri": f"file://{item}"
                    })
                return {
                    "contents": [{
                        "uri": f"file://{path}",
                        "mimeType": "application/json",
                        "text": json.dumps(items, indent=2)
                    }]
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    async def read_codebase_resource(self, path: str) -> Dict[str, Any]:
        """Read codebase resource with intelligent parsing"""
        try:
            # For now, treat as file resource
            return await self.read_file_resource(path)
        except Exception as e:
            return {"error": str(e)}
    
    async def read_document_resource(self, path: str) -> Dict[str, Any]:
        """Read document resource"""
        try:
            # For now, treat as file resource
            return await self.read_file_resource(path)
        except Exception as e:
            return {"error": str(e)}
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in self.tools.values()
            ]
        }
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool"""
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            if name == "read_file":
                return await self.tool_read_file(arguments)
            elif name == "write_file":
                return await self.tool_write_file(arguments)
            elif name == "list_directory":
                return await self.tool_list_directory(arguments)
            elif name == "analyze_code":
                return await self.tool_analyze_code(arguments)
            elif name == "search_documents":
                return await self.tool_search_documents(arguments)
            else:
                return {"error": f"Tool not implemented: {name}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def tool_read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read file tool implementation"""
        path = args.get("path")
        encoding = args.get("encoding", "utf-8")
        
        try:
            if not path or not isinstance(path, str):
                return {"error": "Invalid or missing path argument."}
            # Restrict file access to within ROOT_DIR
            # Prevent absolute paths -- always treat as relative to ROOT_DIR
            user_path = Path(path)
            if user_path.is_absolute():
                return {"error": "Absolute paths are not allowed."}
            full_path = (ROOT_DIR / user_path).resolve()
            root_resolved = ROOT_DIR.resolve()
            try:
                # This will raise ValueError if full_path is not within root_resolved
                full_path.relative_to(root_resolved)
            except ValueError:
                return {"error": "Access to the requested path is not allowed."}
            if not full_path.exists():
                # For security, do not leak existence of files outside root
                return {"error": "Requested file not found or inaccessible."}
            
            async with aiofiles.open(full_path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def tool_write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write file tool implementation"""
        path = args.get("path")
        content = args.get("content")
        encoding = args.get("encoding", "utf-8")
        
        try:
            # Restrict file access to within ROOT_DIR
            if not path or not isinstance(path, str):
                return {"error": "Invalid or missing path argument."}
            user_path = Path(path)
            if user_path.is_absolute():
                return {"error": "Absolute paths are not allowed."}
            full_path = (ROOT_DIR / user_path).resolve()
            root_resolved = ROOT_DIR.resolve()
            try:
                # Ensure full_path is strictly within root_resolved
                full_path.relative_to(root_resolved)
            except ValueError:
                return {"error": "Access to the requested path is not allowed."}
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, 'w', encoding=encoding) as f:
                await f.write(content)
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Successfully wrote to {path}"
                }]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def tool_list_directory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List directory tool implementation"""
        path = args.get("path")
        recursive = args.get("recursive", False)
        
        try:
            # Restrict file access to within ROOT_DIR
            user_path = Path(path)
            full_path = (ROOT_DIR / user_path).resolve()
            root_resolved = ROOT_DIR.resolve()
            if not str(full_path).startswith(str(root_resolved)):
                return {"error": "Access to the requested path is not allowed."}
            if not full_path.exists():
                return {"error": f"Directory not found: {path}"}
            
            if not full_path.is_dir():
                return {"error": f"Path is not a directory: {path}"}
            
            items = []
            if recursive:
                for item in full_path.rglob("*"):
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "path": str(item.relative_to(full_path))
                    })
            else:
                for item in full_path.iterdir():
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "path": str(item.relative_to(full_path))
                    })
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(items, indent=2)
                }]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def tool_analyze_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code tool implementation"""
        path = args.get("path")
        language = args.get("language", "auto")
        
        try:
            # Restrict file access to within ROOT_DIR
            user_path = Path(path)
            full_path = (ROOT_DIR / user_path).resolve()
            root_resolved = ROOT_DIR.resolve()
            if not str(full_path).startswith(str(root_resolved)):
                return {"error": "Access to the requested path is not allowed."}
            if not full_path.exists():
                return {"error": f"Path not found: {path}"}
            
            analysis = {
                "path": str(full_path),
                "language": language,
                "type": "file" if full_path.is_file() else "directory",
                "size": full_path.stat().st_size if full_path.is_file() else None
            }
            
            if full_path.is_file():
                # Basic file analysis
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    analysis["lines"] = len(content.splitlines())
                    analysis["characters"] = len(content)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(analysis, indent=2)
                }]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def tool_search_documents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search documents tool implementation"""
        query = args.get("query")
        limit = args.get("limit", 10)
        
        try:
            # Basic document search (placeholder)
            results = [
                {
                    "title": f"Document matching: {query}",
                    "content": f"This is a placeholder result for query: {query}",
                    "score": 0.95
                }
            ]
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(results[:limit], indent=2)
                }]
            }
        except Exception as e:
            return {"error": str(e)}

mcp_server = MCPServer()

@app.post("/mcp/request")
async def handle_mcp_request(request: MCPRequest):
    return await mcp_server.handle_request(request)

@app.websocket("/mcp/ws")
async def mcp_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            request = MCPRequest(**request_data)
            
            response = await mcp_server.handle_request(request)
            response["id"] = request.id
            
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        await websocket.close(code=1000, reason=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
