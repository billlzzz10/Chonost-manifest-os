#!/usr/bin/env python3
"""
Unified Graph API routes for The Unified Linking Model
Combines Nodes and Edges functionality
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_db
from models.node import Node, NodeType
from models.edge import Edge, EdgeType

router = APIRouter()

# Node Models
class NodeCreate(BaseModel):
    """Request model for creating a node."""
    title: str
    content: Optional[str] = None
    type: NodeType
    document_id: Optional[str] = None
    metadata: Optional[dict] = None

class NodeUpdate(BaseModel):
    """Request model for updating a node."""
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None

class NodeResponse(BaseModel):
    """Response model for a node."""
    id: str
    title: str
    content: Optional[str] = None
    type: str
    metadata: Optional[dict] = None
    created_at: str
    updated_at: Optional[str] = None
    document_id: Optional[str] = None

# Edge Models
class EdgeCreate(BaseModel):
    """Request model for creating an edge."""
    source_id: str
    target_id: str
    type: EdgeType
    label: Optional[str] = None
    strength: Optional[float] = 1.0
    is_explicit: Optional[bool] = True
    metadata: Optional[dict] = None

class EdgeUpdate(BaseModel):
    """Request model for updating an edge."""
    label: Optional[str] = None
    strength: Optional[float] = None
    metadata: Optional[dict] = None

class EdgeResponse(BaseModel):
    """Response model for an edge."""
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

# Node Routes
@router.post("/nodes/", response_model=NodeResponse, summary="Create a new node")
async def create_node(
    node_data: NodeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new node in the database.
    """
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

@router.get("/nodes/", response_model=List[NodeResponse], summary="Get a list of nodes")
async def get_nodes(
    type: Optional[NodeType] = None,
    document_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a list of nodes with optional filtering.
    """
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

@router.get("/nodes/{node_id}", response_model=NodeResponse, summary="Get a specific node")
async def get_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a specific node by its ID.
    """
    try:
        node = await db.get(Node, node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return node.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/nodes/{node_id}", response_model=NodeResponse, summary="Update a node")
async def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates a node's attributes.
    """
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

@router.delete("/nodes/{node_id}", summary="Delete a node")
async def delete_node(
    node_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes a node from the database.
    """
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

# Edge Routes
@router.post("/edges/", response_model=EdgeResponse, summary="Create a new edge")
async def create_edge(
    edge_data: EdgeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new edge between two nodes.
    """
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

@router.get("/edges/", response_model=List[EdgeResponse], summary="Get a list of edges")
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

@router.get("/edges/{edge_id}", response_model=EdgeResponse, summary="Get a specific edge")
async def get_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a specific edge by its ID.
    """
    try:
        edge = await db.get(Edge, edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail="Edge not found")
        return edge.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/edges/{edge_id}", response_model=EdgeResponse, summary="Update an edge")
async def update_edge(
    edge_id: str,
    edge_data: EdgeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates an edge's attributes.
    """
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

@router.delete("/edges/{edge_id}", summary="Delete an edge")
async def delete_edge(
    edge_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes an edge from the database.
    """
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