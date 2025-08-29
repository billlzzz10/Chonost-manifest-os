#!/usr/bin/env python3
"""
Documents API routes for Chonost
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_db
from models.document import Document

router = APIRouter()

class DocumentCreate(BaseModel):
    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    metadata: Optional[dict] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    is_archived: Optional[bool] = None
    metadata: Optional[dict] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    is_archived: bool
    metadata: Optional[dict] = None
    created_at: str
    updated_at: Optional[str] = None
    user_id: Optional[str] = None

@router.post("/", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new document"""
    try:
        document = Document(
            title=document_data.title,
            content=document_data.content,
            file_path=document_data.file_path,
            file_type=document_data.file_type,
            file_size=document_data.file_size,
            metadata=document_data.metadata or {}
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    is_archived: Optional[bool] = None,
    file_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get documents with optional filtering"""
    try:
        query = db.query(Document)
        
        if is_archived is not None:
            query = query.filter(Document.is_archived == is_archived)
        if file_type:
            query = query.filter(Document.file_type == file_type)
        
        documents = await db.execute(
            query.limit(limit).offset(offset)
        )
        return [doc.to_dict() for doc in documents.scalars().all()]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document by ID"""
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a document"""
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document_data.title is not None:
            document.title = document_data.title
        if document_data.content is not None:
            document.content = document_data.content
        if document_data.file_path is not None:
            document.file_path = document_data.file_path
        if document_data.file_type is not None:
            document.file_type = document_data.file_type
        if document_data.file_size is not None:
            document.file_size = document_data.file_size
        if document_data.is_archived is not None:
            document.is_archived = document_data.is_archived
        if document_data.metadata is not None:
            document.metadata = document_data.metadata
        
        await db.commit()
        await db.refresh(document)
        return document.to_dict()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    try:
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        await db.delete(document)
        await db.commit()
        return {"message": "Document deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
