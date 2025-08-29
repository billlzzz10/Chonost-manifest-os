#!/usr/bin/env python3
"""
Edge model for The Unified Linking Model
Represents relationships between nodes
"""

from sqlalchemy import Column, String, DateTime, JSON, Enum, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
import enum

from core.database import Base

class EdgeType(enum.Enum):
    """Types of relationships between nodes"""
    LINK = "link"                    # General link
    REFERENCE = "reference"          # Reference/citation
    CONTAINS = "contains"            # Parent-child relationship
    SIMILAR = "similar"              # Similar content
    OPPOSES = "opposes"              # Opposing concepts
    SUPPORTS = "supports"            # Supporting evidence
    CHARACTER_RELATIONSHIP = "character_relationship"  # Character connections
    LOCATION_CONNECTION = "location_connection"        # Location connections

class Edge(Base):
    """Edge model - represents relationships between nodes"""
    
    __tablename__ = "edges"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source and target nodes
    source_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False)
    
    # Relationship type
    type = Column(Enum(EdgeType), nullable=False)
    
    # Relationship properties
    label = Column(String(200), nullable=True)  # Human-readable label
    strength = Column(Float, default=1.0)       # Relationship strength (0.0 to 1.0)
    is_explicit = Column(Boolean, default=True) # Whether explicitly created by user
    
    # Metadata
    metadata = Column(JSON, nullable=True, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Creator
    user_id = Column(UUID(as_uuid=True), nullable=True)
    
    def __repr__(self):
        return f"<Edge(id={self.id}, source={self.source_id}, target={self.target_id}, type={self.type})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "type": self.type.value,
            "label": self.label,
            "strength": self.strength,
            "is_explicit": self.is_explicit,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": str(self.user_id) if self.user_id else None,
        }
