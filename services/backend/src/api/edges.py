#!/usr/bin/env python3
"""
Edges API routes for The Unified Linking Model
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_db
from models.edge import Edge, EdgeType

router = APIRouter()

class EdgeCreate(BaseModel):
    source_id: str
    target_id: str
    type: EdgeType
    label: Optional[str] = None
    strength: Optional[float] = 1.0
    is_explicit: Optional[bool] = True
    metadata: Optional[dict] = None

class EdgeUpdate(BaseModel):
    label: Optional[str] = None
    strength: Optional[float] = None
    metadata: Optional[dict] = None

class EdgeResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: str
    label: Optional[str] = None
    strength: float
    is_explicit: bool
    metadata: Optional[dict] = None
    created_at: str
    updated_at: Optional[str] = None

@router.post("/", response_model=EdgeResponse)
async def create_edge(
    edge_data: EdgeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new edge"""
    try:
        edge = Edge(
            source_id=edge_data.source_id,
            target_id=edge_data.target_id,
            type=edge_data.type,
            label=edge_data.label,
            strength=edge_data.strength,
            is_explicit=edge_data.is_explicit,
            metadata=edge_data.metadata or {}
        )
        db.add(edge)
        await db.commit()
        await db.refresh(edge)
        return edge.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[EdgeResponse])
async def get_edges(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    type: Optional[EdgeType] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get edges with optional filtering"""
    try:
        query = db.query(Edge)
        
        if source_id:
            query = query.filter(Edge.source_id == source_id)
        if target_id:
            query = query.filter(Edge.target_id == target_id)
        if type:
            query = query.filter(Edge.type == type)
        
        edges = await db.execute(
            query.limit(limit).offset(offset)
        )
        return [edge.to_dict() for edge in edges.scalars().all()]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{edge_id}", response_model=EdgeResponse)
async def get_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific edge by ID"""
    try:
        edge = await db.get(Edge, edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail="Edge not found")
        return edge.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{edge_id}", response_model=EdgeResponse)
async def update_edge(
    edge_id: str,
    edge_data: EdgeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an edge"""
    try:
        edge = await db.get(Edge, edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail="Edge not found")
        
        if edge_data.label is not None:
            edge.label = edge_data.label
        if edge_data.strength is not None:
            edge.strength = edge_data.strength
        if edge_data.metadata is not None:
            edge.metadata = edge_data.metadata
        
        await db.commit()
        await db.refresh(edge)
        return edge.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{edge_id}")
async def delete_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an edge"""
    try:
        edge = await db.get(Edge, edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail="Edge not found")
        
        await db.delete(edge)
        await db.commit()
        return {"message": "Edge deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
