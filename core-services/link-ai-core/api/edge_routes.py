"""
API routes for Edge management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from db_models import Edge, EdgeType

router = APIRouter()

# Pydantic Models for Edge API

class EdgeCreate(BaseModel):
    """Request model for creating an edge."""
    source_id: str
    target_id: str
    type: EdgeType
    label: Optional[str] = None
    strength: Optional[float] = 1.0
    is_explicit: Optional[bool] = True
    manifest: Optional[dict] = None

class EdgeUpdate(BaseModel):
    """Request model for updating an edge."""
    label: Optional[str] = None
    strength: Optional[float] = None
    manifest: Optional[dict] = None

class EdgeResponse(BaseModel):
    """Response model for an edge."""
    id: str
    source_id: str
    target_id: str
    type: EdgeType
    label: Optional[str] = None
    strength: float
    is_explicit: bool
    manifest: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# API Endpoints for Edges

@router.post("/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED, summary="Create a new edge")
async def create_edge(
    edge_data: EdgeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new edge between two nodes.
    """
    try:
        edge = Edge(**edge_data.dict())
        db.add(edge)
        await db.commit()
        await db.refresh(edge)
        return edge
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/edges", response_model=List[EdgeResponse], summary="Get a list of edges")
async def get_edges(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    type: Optional[EdgeType] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a list of edges with optional filtering.
    """
    try:
        query = select(Edge)
        if source_id:
            query = query.where(Edge.source_id == source_id)
        if target_id:
            query = query.where(Edge.target_id == target_id)
        if type:
            query = query.where(Edge.type == type)

        result = await db.execute(query.offset(offset).limit(limit))
        edges = result.scalars().all()
        return edges
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/edges/{edge_id}", response_model=EdgeResponse, summary="Get a specific edge")
async def get_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a specific edge by its ID.
    """
    edge = await db.get(Edge, edge_id)
    if not edge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")
    return edge

@router.put("/edges/{edge_id}", response_model=EdgeResponse, summary="Update an edge")
async def update_edge(
    edge_id: str,
    edge_data: EdgeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates an edge's attributes.
    """
    edge = await db.get(Edge, edge_id)
    if not edge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")

    update_data = edge_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(edge, key, value)

    try:
        await db.commit()
        await db.refresh(edge)
        return edge
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an edge")
async def delete_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes an edge from the database.
    """
    edge = await db.get(Edge, edge_id)
    if not edge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")

    try:
        await db.delete(edge)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))