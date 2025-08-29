#!/usr/bin/env python3
"""
Document model for Chonost
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from core.database import Base

class Document(Base):
    """Document model - represents a document in the system"""
    
    __tablename__ = "documents"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Document properties
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(1000), nullable=True)  # Path to file on disk
    
    # Document metadata
    file_type = Column(String(50), nullable=True)  # md, txt, docx, etc.
    file_size = Column(String(20), nullable=True)
    is_archived = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Owner
    user_id = Column(UUID(as_uuid=True), nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "is_archived": self.is_archived,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": str(self.user_id) if self.user_id else None,
        }
