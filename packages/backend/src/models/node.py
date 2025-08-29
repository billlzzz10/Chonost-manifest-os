#!/usr/bin/env python3
"""
Node model for The Unified Linking Model
Represents any piece of content in the system
"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from core.database import Base

class NodeType(enum.Enum):
    """Types of nodes in the system"""
    DOCUMENT = "document"
    PARAGRAPH = "paragraph"
    CHARACTER = "character"
    LOCATION = "location"
    CONCEPT = "concept"
    IMAGE = "image"
    DIAGRAM = "diagram"
    CODE = "code"
    NOTE = "note"

class Node(Base):
    """Node model - represents any piece of content"""
    
    __tablename__ = "nodes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Content
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    type = Column(Enum(NodeType), nullable=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document_id = Column(UUID(as_uuid=True), nullable=True)  # Parent document
    user_id = Column(UUID(as_uuid=True), nullable=True)      # Owner
    
    def __repr__(self):
        return f"<Node(id={self.id}, title='{self.title}', type={self.type})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "type": self.type.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "document_id": str(self.document_id) if self.document_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
        }
