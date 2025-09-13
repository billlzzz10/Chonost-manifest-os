#!/usr/bin/env python3
"""
Main API router for the Chonost application.
"""

from fastapi import APIRouter
from api.mongodb_routes import router as mongodb_router
from api.ai_routes import router as ai_router

router = APIRouter()

# Include other routers
router.include_router(mongodb_router, prefix="/mongodb", tags=["mongodb"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])

@router.get("/", summary="Root endpoint")
async def root():
    """
    Provides basic information about the API.
    """
    return {"message": "Chonost API", "version": "1.0.0"}

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Performs a basic health check on the service.
    """
    return {"status": "healthy", "service": "chonost-api"}
