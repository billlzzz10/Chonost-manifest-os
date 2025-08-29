from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import String, Integer, Boolean, DateTime, Text
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(255), unique=True, nullable=False)
    email = db.Column(String(255), unique=True, nullable=False)
    password_hash = db.Column(String(255))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    files = db.relationship('File', backref='user', lazy=True, cascade='all, delete-orphan')
    workflows = db.relationship('Workflow', backref='user', lazy=True, cascade='all, delete-orphan')
    service_connections = db.relationship('ServiceConnection', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)
    original_name = db.Column(Text, nullable=False)
    filename = db.Column(Text, nullable=False)
    file_path = db.Column(Text, nullable=False)
    file_type = db.Column(String(50), nullable=False)
    file_size = db.Column(Integer, nullable=False)
    mime_type = db.Column(String(255), nullable=False)
    upload_type = db.Column(String(50), default='general')
    processed_data = db.Column(JSONB)  # PostgreSQL JSONB for better performance
    created_at = db.Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<File {self.original_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_name': self.original_name,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_type': self.upload_type,
            'processed_data': self.processed_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
