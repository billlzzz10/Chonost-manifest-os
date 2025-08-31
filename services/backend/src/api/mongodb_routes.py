#!/usr/bin/env python3
"""
MongoDB API routes for Chonost
"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from pydantic import BaseModel
from bson import ObjectId

from core.mongodb import get_mongodb

router = APIRouter()

class DocumentCreate(BaseModel):
    title: str
    content: str
    metadata: Dict[str, Any] = {}

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Create a new document in MongoDB"""
    try:
        collection = db.documents
        result = await collection.insert_one({
            "title": document.title,
            "content": document.content,
            "metadata": document.metadata,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        })
        
        # Get the created document
        created_doc = await collection.find_one({"_id": result.inserted_id})
        
        return DocumentResponse(
            id=str(created_doc["_id"]),
            title=created_doc["title"],
            content=created_doc["content"],
            metadata=created_doc["metadata"],
            created_at=created_doc["created_at"],
            updated_at=created_doc["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    limit: int = 100,
    skip: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get documents from MongoDB"""
    try:
        collection = db.documents
        cursor = collection.find().skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        return [
            DocumentResponse(
                id=str(doc["_id"]),
                title=doc["title"],
                content=doc["content"],
                metadata=doc["metadata"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"]
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get a specific document by ID"""
    try:
        collection = db.documents
        document = await collection.find_one({"_id": ObjectId(document_id)})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=str(document["_id"]),
            title=document["title"],
            content=document["content"],
            metadata=document["metadata"],
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document: DocumentCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Update a document"""
    try:
        collection = db.documents
        result = await collection.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "title": document.title,
                    "content": document.content,
                    "metadata": document.metadata,
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get the updated document
        updated_doc = await collection.find_one({"_id": ObjectId(document_id)})
        
        return DocumentResponse(
            id=str(updated_doc["_id"]),
            title=updated_doc["title"],
            content=updated_doc["content"],
            metadata=updated_doc["metadata"],
            created_at=updated_doc["created_at"],
            updated_at=updated_doc["updated_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Delete a document"""
    try:
        collection = db.documents
        result = await collection.delete_one({"_id": ObjectId(document_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
