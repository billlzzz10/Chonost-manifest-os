"""
API routes for Manuscript management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from db_models import Manuscript

router = APIRouter()

# Pydantic Models for Manuscript API

class ManuscriptCreate(BaseModel):
    """Request model for creating a manuscript."""
    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    manifest: Optional[dict] = None
    user_id: Optional[str] = None

class ManuscriptUpdate(BaseModel):
    """Request model for updating a manuscript."""
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    is_archived: Optional[bool] = None
    manifest: Optional[dict] = None

class ManuscriptResponse(BaseModel):
    """Response model for a manuscript."""
    id: str
    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[str] = None
    is_archived: bool
    manifest: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[str] = None

    class Config:
        orm_mode = True

# API Endpoints for Manuscripts

@router.post("/manuscripts", response_model=ManuscriptResponse, status_code=status.HTTP_201_CREATED, summary="Create a new manuscript")
async def create_manuscript(
    manuscript_data: ManuscriptCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new manuscript in the database.
    """
    try:
        manuscript_payload = manuscript_data.dict(exclude_unset=True)
        manuscript = Manuscript(**manuscript_payload)
        db.add(manuscript)
        await db.commit()
        await db.refresh(manuscript)
        return manuscript
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/manuscripts", response_model=List[ManuscriptResponse], summary="Get a list of manuscripts")
async def get_manuscripts(
    is_archived: Optional[bool] = None,
    user_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a list of manuscripts with optional filtering.
    """
    # Basic parameter validation to avoid unexpected DB behaviour or abuse
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="`limit` must be between 1 and 1000")
    if offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="`offset` must be >= 0")
    try:
        query = select(Manuscript)
        if is_archived is not None:
            query = query.where(Manuscript.is_archived == is_archived)
        if user_id:
            query = query.where(Manuscript.user_id == user_id)

        result = await db.execute(query.offset(offset).limit(limit))
        manuscripts = result.scalars().all()
        return manuscripts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/manuscripts/{manuscript_id}", response_model=ManuscriptResponse, summary="Get a specific manuscript")
async def get_manuscript(
    manuscript_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Gets a specific manuscript by its ID.
    """
    manuscript = await db.get(Manuscript, manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscript not found")
    return manuscript

@router.put("/manuscripts/{manuscript_id}", response_model=ManuscriptResponse, summary="Update a manuscript")
async def update_manuscript(
    manuscript_id: str,
    manuscript_data: ManuscriptUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates a manuscript's attributes.
    """
    manuscript = await db.get(Manuscript, manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscript not found")

    update_data = manuscript_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(manuscript, key, value)

    try:
        await db.commit()
        await db.refresh(manuscript)
        return manuscript
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/manuscripts/{manuscript_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a manuscript")
async def delete_manuscript(
    manuscript_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes a manuscript from the database.
    """
    manuscript = await db.get(Manuscript, manuscript_id)
    if not manuscript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscript not found")

    try:
        await db.delete(manuscript)
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))