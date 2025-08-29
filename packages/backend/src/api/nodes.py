#!/usr/bin/env python3
"""
Nodes API routes for The Unified Linking Model
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_db
from models.node import Node, NodeType

router = APIRouter()

class NodeCreate(BaseModel):
    title: str
    content: Optional[str] = None
    type: NodeType
    document_id: Optional[str] = None
    metadata: Optional[dict] = None

class NodeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None

class NodeResponse(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    type: str
    metadata: Optional[dict] = None
    created_at: str
    updated_at: Optional[str] = None
    document_id: Optional[str] = None

@router.post("/", response_model=NodeResponse)
async def create_node(
    node_data: NodeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new node"""
    try:
        node = Node(
            title=node_data.title,
            content=node_data.content,
            type=node_data.type,
            document_id=node_data.document_id,
            metadata=node_data.metadata or {}
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[NodeResponse])
async def get_nodes(
    type: Optional[NodeType] = None,
    document_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get nodes with optional filtering"""
    try:
        query = db.query(Node)
        
        if type:
            query = query.filter(Node.type == type)
        if document_id:
            query = query.filter(Node.document_id == document_id)
        
        nodes = await db.execute(
            query.limit(limit).offset(offset)
        )
        return [node.to_dict() for node in nodes.scalars().all()]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific node by ID"""
    try:
        node = await db.get(Node, node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return node.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a node"""
    try:
        node = await db.get(Node, node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        if node_data.title is not None:
            node.title = node_data.title
        if node_data.content is not None:
            node.content = node_data.content
        if node_data.metadata is not None:
            node.metadata = node_data.metadata
        
        await db.commit()
        await db.refresh(node)
        return node.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{node_id}")
async def delete_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a node"""
    try:
        node = await db.get(Node, node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        await db.delete(node)
        await db.commit()
        return {"message": "Node deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
