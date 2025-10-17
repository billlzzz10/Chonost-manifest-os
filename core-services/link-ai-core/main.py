"""
Chonost Manuscript OS - Main API Entry Point
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings
from database import create_db_and_tables
from api import manuscript_routes, node_routes, edge_routes

# Create FastAPI app
app = FastAPI(
    title="Chonost Manuscript OS API",
    description="The core API for managing manuscripts, nodes, relationships, and AI interactions.",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize settings
settings = Settings()

@app.on_event("startup")
async def on_startup():
    """
    Event handler for application startup.
    Creates database tables if they don't exist.
    """
    print("Creating database and tables...")
    await create_db_and_tables()
    print("Database and tables created successfully.")

# Include the API routers
app.include_router(manuscript_routes.router, prefix="/api/v1", tags=["Manuscripts"])
app.include_router(node_routes.router, prefix="/api/v1", tags=["Nodes"])
app.include_router(edge_routes.router, prefix="/api/v1", tags=["Edges"])

# Core health check endpoint
@app.get("/health")
async def health_check():
    """
    A health check endpoint for the service.
    """
    return {
        "status": "healthy",
        "service": "Chonost Manuscript OS API",
        "version": "3.0.0"
    }

def run_app(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """
    Run the Chonost Manuscript OS API application.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
    """
    print("🚀 Starting Chonost Manuscript OS API...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Docs available at: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_app()