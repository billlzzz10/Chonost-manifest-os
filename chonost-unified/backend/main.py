#!/usr/bin/env python3
"""
Chonost Unified Backend Server
รวม FastAPI server สำหรับทั้ง Main App และ MCP Integration
"""

import uvicorn
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Chonost Unified Backend",
    description="Unified backend for Chonost Desktop App and MCP Platform",
    version="2.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:1420",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:1420",
        "tauri://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chonost-unified-backend",
        "version": "2.2.0"
    }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "name": "Chonost Unified API",
        "version": "2.2.0",
        "endpoints": {
            "health": "/health",
            "api_info": "/api/info",
            "mcp_tools": "/api/mcp/tools",
            "mcp_call": "/api/mcp/call",
            "rag_search": "/api/rag/search",
            "knowledge_graph": "/api/knowledge/graph"
        }
    }

# MCP Integration - using real MCP orchestrator
try:
    from .mcp.main import app as mcp_app
    from .mcp.mcp.registry import MCPRegistry
    from .mcp.mcp.client import MCPClient

    # Initialize MCP components
    mcp_registry = MCPRegistry()
    mcp_client = MCPClient()

    @app.get("/api/mcp/tools")
    async def get_mcp_tools():
        """Get available MCP tools from real orchestrator"""
        try:
            # Get tools from MCP registry
            tools = await mcp_registry.list_tools()
            return {
                "tools": tools,
                "source": "mcp-orchestrator"
            }
        except Exception as e:
            # Fallback to placeholder data
            logger.warning(f"MCP orchestrator not available: {e}")
            return {
                "tools": [
                    {
                        "name": "fs.semantic_search",
                        "description": "Semantic search in codebase",
                        "category": "filesystem"
                    },
                    {
                        "name": "gh.pr_create_smart",
                        "description": "Create smart pull request",
                        "category": "github"
                    }
                ],
                "source": "placeholder",
                "error": str(e)
            }

    @app.post("/api/mcp/call")
    async def call_mcp_tool(tool_call: dict):
        """Call MCP tool through real orchestrator"""
        try:
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})

            # Call tool through MCP client
            result = await mcp_client.call_tool(tool_name, parameters)

            return {
                "success": True,
                "result": result,
                "source": "mcp-orchestrator"
            }
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "error"
            }

except ImportError as e:
    logger.warning(f"MCP orchestrator not available: {e}")

    # Fallback endpoints
    @app.get("/api/mcp/tools")
    async def get_mcp_tools_fallback():
        """Get available MCP tools (fallback)"""
        return {
            "tools": [
                {
                    "name": "fs.semantic_search",
                    "description": "Semantic search in codebase",
                    "category": "filesystem"
                },
                {
                    "name": "gh.pr_create_smart",
                    "description": "Create smart pull request",
                    "category": "github"
                }
            ],
            "source": "fallback"
        }

    @app.post("/api/mcp/call")
    async def call_mcp_tool_fallback(tool_call: dict):
        """Call MCP tool (fallback)"""
        return {
            "success": False,
            "error": "MCP orchestrator not available",
            "source": "fallback"
        }

# Placeholder for RAG search
@app.get("/api/rag/search")
async def rag_search(query: str = "", limit: int = 5):
    """RAG search endpoint"""
    return {
        "query": query,
        "results": [
            {
                "title": "Sample Document",
                "content": "Sample content...",
                "similarity": 0.85
            }
        ],
        "total": 1
    }

# Placeholder for knowledge graph
@app.get("/api/knowledge/graph")
async def knowledge_graph():
    """Knowledge graph endpoint"""
    return {
        "nodes": [
            {
                "id": "1",
                "title": "Chonost Overview",
                "type": "document",
                "connections": ["2", "3"]
            }
        ],
        "edges": []
    }

# WebSocket endpoint for real-time communication
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now, implement real-time features later
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

def run_app():
    """Run the FastAPI application"""
    logger.info("🚀 Starting Chonost Unified Backend Server")
    logger.info("📡 API docs available at: http://localhost:8000/api/docs")

    # Check if we're running from backend directory or parent directory
    import os
    current_dir = os.path.basename(os.getcwd())

    if current_dir == "backend":
        # Running from backend directory
        module_path = "main:app"
    else:
        # Running from parent directory
        module_path = "backend.main:app"

    uvicorn.run(
        module_path,
        host="0.0.0.0",
        port=8002,  # เปลี่ยน port เป็น 8002 เพื่อหลีกเลี่ยง conflict
        reload=False,  # ปิด auto-reload เพื่อป้องกัน connection reset
        log_level="info"
    )

if __name__ == "__main__":
    run_app()
