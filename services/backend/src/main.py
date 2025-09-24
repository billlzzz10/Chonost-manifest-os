#!/usr/bin/env python3
"""
Main FastAPI application for Chonost Backend
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import our modules
try:
    from core.config import settings
except ImportError:
    # Fallback config
    class Settings:
        APP_NAME = "Chonost API"
        VERSION = "1.0.0"
        DEBUG = True
        HOST = "0.0.0.0"
        PORT = 8000
        # Avoid permissive wildcard in production.
        ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:1420"]
    settings = Settings()

try:
    from core.database import engine, Base
except ImportError:
    engine = None
    Base = None

try:
    from api.routes import router
except ImportError:
    from fastapi import APIRouter
    router = APIRouter()
    
    @router.get("/")
    async def root():
        return {"message": "Chonost API", "version": "1.0.0"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Chonost Backend...")
    
    # Create database tables if available
    if engine and Base:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Database initialized")
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
    
    print("✅ Backend started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Chonost Backend...")
    if engine:
        await engine.dispose()
    print("✅ Backend shutdown")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return JSONResponse({
            "status": "healthy",
            "service": "chonost-api",
            "version": settings.VERSION,
            "timestamp": "2025-08-30T00:00:00Z"
        })
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chonost Manuscript OS API",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Chonost Backend on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
