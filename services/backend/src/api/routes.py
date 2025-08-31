#!/usr/bin/env python3
"""
Main API routes for Chonost
"""

from fastapi import APIRouter
from api.mongodb_routes import router as mongodb_router
from api.ai_routes import router as ai_router

router = APIRouter()

# Include other routers
router.include_router(mongodb_router, prefix="/mongodb", tags=["mongodb"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Chonost API", "version": "1.0.0"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chonost-api"}
