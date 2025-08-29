#!/usr/bin/env python3
"""
Main API router for Chonost
"""

from fastapi import APIRouter
from api.health import router as health_router
from api.nodes import router as nodes_router
from api.edges import router as edges_router
from api.documents import router as documents_router
from api.mongodb_routes import router as mongodb_router

router = APIRouter()

# Include sub-routers
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(nodes_router, prefix="/nodes", tags=["nodes"])
router.include_router(edges_router, prefix="/edges", tags=["edges"])
router.include_router(documents_router, prefix="/documents", tags=["documents"])
router.include_router(mongodb_router, prefix="/mongodb", tags=["mongodb"])
