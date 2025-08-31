from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class ServiceConnection(db.Model):
    __tablename__ = 'service_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_name = db.Column(db.String(50), nullable=False)  # 'notion', 'google_drive', 'dropbox', etc.
    service_display_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.Text)  # Encrypted API key
    access_token = db.Column(db.Text)  # Encrypted access token
    refresh_token = db.Column(db.Text)  # Encrypted refresh token
    token_expires_at = db.Column(db.DateTime)
    connection_config = db.Column(db.JSON)  # Service-specific configuration
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='service_connections')
    
    def __repr__(self):
        return f'<ServiceConnection {self.id}: {self.service_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'service_display_name': self.service_display_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'has_valid_token': self.token_expires_at is None or self.token_expires_at > datetime.utcnow()
        }

class ServiceAction(db.Model):
    __tablename__ = 'service_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    connection_id = db.Column(db.Integer, db.ForeignKey('service_connections.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # 'read', 'write', 'create', 'update', 'delete'
    action_name = db.Column(db.String(100), nullable=False)  # Human-readable action name
    endpoint = db.Column(db.String(200))  # API endpoint
    method = db.Column(db.String(10), default='GET')  # HTTP method
    parameters = db.Column(db.JSON)  # Action parameters
    response_format = db.Column(db.JSON)  # Expected response format
    is_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    connection = db.relationship('ServiceConnection', backref='available_actions')
    
    def __repr__(self):
        return f'<ServiceAction {self.id}: {self.action_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'action_type': self.action_type,
            'action_name': self.action_name,
            'endpoint': self.endpoint,
            'method': self.method,
            'parameters': self.parameters,
            'response_format': self.response_format,
            'is_enabled': self.is_enabled
        }

