"""
SQLAlchemy database models for the Chonost Manuscript OS.
"""

import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    Enum,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Manuscript(Base):
    __tablename__ = "manuscripts"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(1024), nullable=True)
    file_type = Column(String(50), nullable=True)
    file_size = Column(String(50), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    manifest = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String, nullable=True) # Assuming user ID is a string for now

    nodes = relationship("Node", back_populates="manuscript", cascade="all, delete-orphan")

class NodeType(enum.Enum):
    CHARACTER = "character"
    LOCATION = "location"
    EVENT = "event"
    ITEM = "item"
    CONCEPT = "concept"
    NOTE = "note"

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    type = Column(Enum(NodeType), nullable=False)
    manifest = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    manuscript_id = Column(String, ForeignKey("manuscripts.id"), nullable=True)
    manuscript = relationship("Manuscript", back_populates="nodes")

    source_edges = relationship("Edge", foreign_keys="[Edge.source_id]", back_populates="source_node", cascade="all, delete-orphan")
    target_edges = relationship("Edge", foreign_keys="[Edge.target_id]", back_populates="target_node", cascade="all, delete-orphan")

class EdgeType(enum.Enum):
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    LEADS_TO = "leads_to"
    CONFLICTS_WITH = "conflicts_with"
    SUPPORTS = "supports"
    LOCATION_OF = "location_of"

class Edge(Base):
    __tablename__ = "edges"

    id = Column(String, primary_key=True, default=generate_uuid)
    source_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    target_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    type = Column(Enum(EdgeType), nullable=False)
    label = Column(String(255), nullable=True)
    strength = Column(Float, default=1.0)
    is_explicit = Column(Boolean, default=True)
    manifest = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    source_node = relationship("Node", foreign_keys=[source_id], back_populates="source_edges")
    target_node = relationship("Node", foreign_keys=[target_id], back_populates="target_edges")