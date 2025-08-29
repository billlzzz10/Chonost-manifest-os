#!/usr/bin/env python3
"""
Main FastAPI application for Chonost Backend
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import engine, Base
from core.mongodb import mongodb_manager
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Chonost Backend...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Connect to MongoDB
    try:
        await mongodb_manager.connect()
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
    
    print("✅ Backend started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Chonost Backend...")
    await mongodb_manager.disconnect()
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
        # Check MongoDB connection
        mongodb_status = "connected" if mongodb_manager.client else "disconnected"
        
        return JSONResponse({
            "status": "healthy",
            "service": "chonost-api",
            "version": settings.VERSION,
            "mongodb": mongodb_status
        })
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
