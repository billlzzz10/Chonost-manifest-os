"""
MCP AI Orchestrator - Main Entry Point.
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

# Import Phase 2: Project Manifest System components
try:
    from .phase2.file_system_watcher import FileSystemWatcher
    from .phase2.entity_extraction import EntityExtractor
    from .phase2.vector_db import VectorDatabase

    # Initialize Phase 2 components
    manifest_watcher = None  # Will be initialized when started
    entity_extractor = EntityExtractor()
    vector_db = VectorDatabase()

    print("✅ Phase 2: Project Manifest System components loaded successfully")

except ImportError as e:
    print(f"Warning: Phase 2 components not available: {e}")
    manifest_watcher = None
    entity_extractor = None
    vector_db = None

# API Endpoints for MCP Orchestrator

@app.get("/health")
async def health_check():
    """
    A health check endpoint for the service.
    """
    return {
        "status": "healthy",
        "service": "mcp-orchestrator",
        "phase2": {
            "entity_extractor": "available" if entity_extractor else "unavailable",
            "vector_db": "available" if vector_db else "unavailable",
            "watcher": "available" if manifest_watcher else "unavailable"
        },
        "version": "2.2.0"
    }

@app.get("/mcp/servers")
async def list_servers():
    """
    Lists the available MCP servers.
    """
    if not mcp_registry:
        raise HTTPException(status_code=503, detail="MCP registry not available")

    try:
        servers = await mcp_registry.list_servers()
        return {"servers": servers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list servers: {str(e)}")

@app.get("/mcp/tools")
async def list_tools():
    """
    Lists the available MCP tools.
    """
    if not mcp_registry:
        raise HTTPException(status_code=503, detail="MCP registry not available")

    try:
        tools = await mcp_registry.list_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@app.post("/mcp/call")
async def call_tool(tool_call: dict):
    """
    Executes an MCP tool.
    """
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
    """
    Gets the status of the MCP orchestrator.
        "phase2": {
            "entity_extractor": "available" if entity_extractor else "unavailable",
            "vector_db": "available" if vector_db else "unavailable",
            "watcher": "running" if manifest_watcher and manifest_watcher.is_alive() else "stopped"
        },
    """
    return {
        "status": "operational" if mcp_registry and mcp_client else "degraded",
        "registry": "available" if mcp_registry else "unavailable",
        "client": "available" if mcp_client else "unavailable",
        "settings": settings.dict() if settings else None
    }
# Phase 2: Project Manifest System API Endpoints

@app.post("/manifest/start-watcher")
async def start_manifest_watcher(request: dict):
    """
    Start the file system watcher for project manifest.
    """
    global manifest_watcher

    if not entity_extractor or not vector_db:
        raise HTTPException(status_code=503, detail="Phase 2 components not available")

    try:
        watch_path = request.get("path", ".")
        if manifest_watcher:
            manifest_watcher.stop()

        manifest_watcher = FileSystemWatcher(
            watch_path=watch_path,
            entity_extractor=entity_extractor,
            vector_db=vector_db
        )
        manifest_watcher.start()

        return {
            "success": True,
            "message": f"Manifest watcher started for path: {watch_path}",
            "status": "running"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start watcher: {str(e)}")

@app.post("/manifest/stop-watcher")
async def stop_manifest_watcher():
    """
    Stop the file system watcher.
    """
    global manifest_watcher

    try:
        if manifest_watcher:
            manifest_watcher.stop()
            manifest_watcher = None
            return {
                "success": True,
                "message": "Manifest watcher stopped",
                "status": "stopped"
            }
        else:
            return {
                "success": True,
                "message": "No watcher running",
                "status": "not_running"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop watcher: {str(e)}")

@app.get("/manifest/search")
async def search_manifest(query: str, limit: int = 10):
    """
    Search for entities in the manifest.
    """
    if not vector_db:
        raise HTTPException(status_code=503, detail="Vector database not available")

    try:
        results = vector_db.search_similar(query, limit=limit)
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/manifest/extract")
async def extract_entities(request: dict):
    """
    Extract entities from a file.
    """
    if not entity_extractor:
        raise HTTPException(status_code=503, detail="Entity extractor not available")

    try:
        file_path = request.get("file_path")
        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")

        entities = entity_extractor.extract_entities(file_path)

        # Store in vector database if available
        if vector_db:
            stored_count = vector_db.store_entities_batch(entities)
        else:
            stored_count = 0

        return {
            "success": True,
            "file_path": file_path,
            "entities_extracted": len(entities),
            "entities_stored": stored_count,
            "entities": [entity.__dict__ for entity in entities[:50]]  # Return first 50
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.get("/manifest/stats")
async def get_manifest_stats():
    """
    Get manifest system statistics.
    """
    try:
        stats = {}

        if vector_db:
            stats["vector_db"] = vector_db.get_stats()
        else:
            stats["vector_db"] = {"status": "unavailable"}

        stats["watcher"] = {
            "status": "running" if manifest_watcher and manifest_watcher.is_alive() else "stopped"
        }

        stats["components"] = {
            "entity_extractor": "available" if entity_extractor else "unavailable",
            "vector_db": "available" if vector_db else "unavailable",
            "watcher": "available" if manifest_watcher else "unavailable"
        }

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/manifest/entities/{entity_type}")
async def get_entities_by_type(entity_type: str, limit: int = 50):
    """
    Get entities by type.
    """
    if not vector_db:
        raise HTTPException(status_code=503, detail="Vector database not available")

    try:
        results = vector_db.search_by_type(entity_type, limit=limit)
        return {
            "success": True,
            "entity_type": entity_type,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entities: {str(e)}")

@app.get("/manifest/file/{file_path:path}")
async def get_file_entities(file_path: str):
    """
    Get all entities from a specific file.
    """
    if not vector_db:
        raise HTTPException(status_code=503, detail="Vector database not available")

    try:
        results = vector_db.search_by_file(file_path)
        return {
            "success": True,
            "file_path": file_path,
            "results": results,
            "count": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file entities: {str(e)}")


def run_app(host: str = "0.0.0.0", port: int = 8765, reload: bool = True) -> None:
    print(f"🔧 Phase 2 Manifest endpoints: http://{host}:{port}/manifest")
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
