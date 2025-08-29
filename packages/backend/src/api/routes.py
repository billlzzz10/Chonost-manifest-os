#!/usr/bin/env python3
"""
API routes for Chonost
"""

from fastapi import APIRouter

from .nodes import router as nodes_router
from .edges import router as edges_router
from .documents import router as documents_router
from .health import router as health_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router, tags=["health"])
api_router.include_router(nodes_router, prefix="/nodes", tags=["nodes"])
api_router.include_router(edges_router, prefix="/edges", tags=["edges"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
