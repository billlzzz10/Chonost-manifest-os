from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db
import json

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Workflow configuration
    trigger_config = db.Column(db.JSON)  # Trigger configuration
    steps_config = db.Column(db.JSON)    # Steps configuration
    
    # Relationships
    executions = db.relationship('WorkflowExecution', backref='workflow', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Workflow {self.id}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'trigger_config': self.trigger_config,
            'steps_config': self.steps_config,
            'execution_count': len(self.executions)
        }

class WorkflowExecution(db.Model):
    __tablename__ = 'workflow_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    execution_data = db.Column(db.JSON)  # Input/output data for the execution
    
    def __repr__(self):
        return f'<WorkflowExecution {self.id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'execution_data': self.execution_data
        }

class ServiceConnection(db.Model):
    __tablename__ = 'service_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)  # notion, google_drive, etc.
    connection_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Connection configuration (encrypted)
    config = db.Column(db.JSON)  # API keys, tokens, etc.
    
    def __repr__(self):
        return f'<ServiceConnection {self.id}: {self.service_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'connection_name': self.connection_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'has_config': bool(self.config)
        }

class AutomationTemplate(db.Model):
    __tablename__ = 'automation_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # document, data, notification, etc.
    complexity = db.Column(db.String(20), default='medium')  # easy, medium, hard
    services = db.Column(db.JSON)  # List of required services
    template_config = db.Column(db.JSON)  # Template configuration
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationTemplate {self.id}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'complexity': self.complexity,
            'services': self.services,
            'template_config': self.template_config,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

