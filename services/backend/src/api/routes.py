#!/usr/bin/env python3
"""
Main API router for the Chonost application.
"""

from fastapi import APIRouter
from api.mongodb_routes import router as mongodb_router
from api.ai_routes import router as ai_router
try:
    # Integrated routes (FastAPI APIRouter) defined outside api package
    from integrated_routes import intergrated_router as integrated_router
except Exception:  # fallback if module path differs
    integrated_router = None

router = APIRouter()

# Include other routers
router.include_router(mongodb_router, prefix="/mongodb", tags=["mongodb"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])
if integrated_router is not None:
    router.include_router(integrated_router)

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
