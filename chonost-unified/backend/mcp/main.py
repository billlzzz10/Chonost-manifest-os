"""
MCP AI Orchestrator - Main Entry Point
"""

import asyncio
import uvicorn
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app for MCP orchestrator
app = FastAPI(
    title="MCP AI Orchestrator",
    description="AI-powered MCP (Model Context Protocol) Orchestrator",
    version="2.2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import MCP components from unified backend
try:
    from .mcp.registry import MCPRegistry
    from .mcp.client import MCPClient
    from .config import Settings

    # Initialize MCP components
    settings = Settings()
    mcp_registry = MCPRegistry()
    mcp_client = MCPClient()  # Unified client that handles server selection automatically

except ImportError as e:
    print(f"Warning: MCP components not available: {e}")
    mcp_registry = None
    mcp_client = None
    settings = None

# API Endpoints for MCP Orchestrator

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mcp-orchestrator",
        "version": "2.2.0"
    }

@app.get("/mcp/servers")
async def list_servers():
    """List available MCP servers"""
    if not mcp_registry:
        raise HTTPException(status_code=503, detail="MCP registry not available")

    try:
        servers = await mcp_registry.list_servers()
        return {"servers": servers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list servers: {str(e)}")

@app.get("/mcp/tools")
async def list_tools():
    """List available MCP tools"""
    if not mcp_registry:
        raise HTTPException(status_code=503, detail="MCP registry not available")

    try:
        tools = await mcp_registry.list_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@app.post("/mcp/call")
async def call_tool(tool_call: dict):
    """Execute MCP tool"""
    if not mcp_client:
        raise HTTPException(status_code=503, detail="MCP client not available")

    try:
        tool_name = tool_call.get("tool")
        parameters = tool_call.get("parameters", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name is required")

        result = await mcp_client.call_tool(tool_name, parameters)
        return {
            "success": True,
            "result": result,
            "tool": tool_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.get("/mcp/status")
async def get_status():
    """Get MCP orchestrator status"""
    return {
        "status": "operational" if mcp_registry and mcp_client else "degraded",
        "registry": "available" if mcp_registry else "unavailable",
        "client": "available" if mcp_client else "unavailable",
        "settings": settings.dict() if settings else None
    }

def run_app(host: str = "0.0.0.0", port: int = 8765, reload: bool = True) -> None:
    """
    Run the MCP AI Orchestrator application.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    print("🚀 Starting MCP AI Orchestrator...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"🔧 MCP Orchestrator endpoint: http://{host}:{port}/mcp")
    
    uvicorn.run(
        "backend.mcp.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

def run_mcp_server() -> None:
    """Run the MCP Server specifically."""
    run_app()

if __name__ == "__main__":
    run_app()
