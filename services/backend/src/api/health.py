#!/usr/bin/env python3
"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

router = APIRouter()

@router.get("/health", summary="Basic health check")
async def health_check():
    """
    Performs a basic health check on the service.
    """
    return {
        "status": "healthy",
        "service": "chonost-backend",
        "version": "1.0.0"
    }

@router.get("/health/db", summary="Database health check")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Performs a health check on the database connection.
    """
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
