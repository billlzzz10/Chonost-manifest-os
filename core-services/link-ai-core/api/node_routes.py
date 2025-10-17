"""
API routes for Node management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from database import get_db
from db_models import Node, NodeType

router = APIRouter()

# Pydantic Models for Node API

class NodeCreate(BaseModel):
    """Request model for creating a node."""
    title: str
    content: Optional[str] = None
    type: NodeType
    manuscript_id: Optional[str] = None
    manifest: Optional[dict] = None

class NodeUpdate(BaseModel):
    """Request model for updating a node."""
    title: Optional[str] = None
    content: Optional[str] = None
    manifest: Optional[dict] = None

class NodeResponse(BaseModel):
    """Response model for a node."""
    id: str
    title: str
    content: Optional[str] = None
    type: NodeType
    manifest: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    manuscript_id: Optional[str] = None

    class Config:
        orm_mode = True

# API Endpoints for Nodes

@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED, summary="Create a new node")
async def create_node(
    node_data: NodeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new node in the database.
    """
    try:
        node = Node(**node_data.dict(exclude_none=True))
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/nodes", response_model=List[NodeResponse], summary="Get a list of nodes")
async def get_nodes(
    type: Optional[NodeType] = None,
    manuscript_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a list of nodes with optional filtering.
    """
    try:
        query = select(Node)
        if type:
            query = query.where(Node.type == type)
        if manuscript_id:
            query = query.where(Node.manuscript_id == manuscript_id)

        result = await db.execute(query.offset(offset).limit(limit))
        nodes = result.scalars().all()
        return nodes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/nodes/{node_id}", response_model=NodeResponse, summary="Get a specific node")
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a specific node by its ID.
    """
    node = await db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node

@router.put("/nodes/{node_id}", response_model=NodeResponse, summary="Update a node")
async def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates a node's attributes.
    """
    node = await db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    update_data = node_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(node, key, value)

    try:
        await db.commit()
        await db.refresh(node)
        return node
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a node")
async def delete_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes a node from the database.
    """
    node = await db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    try:
        await db.delete(node)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))