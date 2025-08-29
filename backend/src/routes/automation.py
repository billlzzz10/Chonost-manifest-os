from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    trigger_type = db.Column(db.String(50), nullable=False)  # 'manual', 'schedule', 'webhook', 'event'
    trigger_config = db.Column(db.JSON)  # Trigger configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run_at = db.Column(db.DateTime)
    run_count = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', backref='workflows')
    steps = db.relationship('WorkflowStep', backref='workflow', lazy=True, cascade='all, delete-orphan', order_by='WorkflowStep.order')
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
            'trigger_type': self.trigger_type,
            'trigger_config': self.trigger_config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'run_count': self.run_count,
            'step_count': len(self.steps)
        }

class WorkflowStep(db.Model):
    __tablename__ = 'workflow_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    step_type = db.Column(db.String(50), nullable=False)  # 'action', 'condition', 'delay', 'loop'
    service_connection_id = db.Column(db.Integer, db.ForeignKey('service_connections.id'))
    action_config = db.Column(db.JSON, nullable=False)  # Step configuration
    condition_config = db.Column(db.JSON)  # Condition configuration for conditional steps
    is_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    service_connection = db.relationship('ServiceConnection', backref='workflow_steps')
    
    def __repr__(self):
        return f'<WorkflowStep {self.id}: {self.step_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_id': self.workflow_id,
            'order': self.order,
            'step_type': self.step_type,
            'service_connection_id': self.service_connection_id,
            'action_config': self.action_config,
            'condition_config': self.condition_config,
            'is_enabled': self.is_enabled
        }

class WorkflowExecution(db.Model):
    __tablename__ = 'workflow_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflows.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='running')  # 'running', 'completed', 'failed', 'cancelled'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    execution_log = db.Column(db.JSON)  # Detailed execution log
    trigger_data = db.Column(db.JSON)  # Data that triggered the execution
    
    # Relationships
    step_executions = db.relationship('StepExecution', backref='workflow_execution', lazy=True, cascade='all, delete-orphan')
    
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
            'execution_log': self.execution_log,
            'trigger_data': self.trigger_data,
            'duration': (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None
        }

class StepExecution(db.Model):
    __tablename__ = 'step_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    workflow_execution_id = db.Column(db.Integer, db.ForeignKey('workflow_executions.id'), nullable=False)
    workflow_step_id = db.Column(db.Integer, db.ForeignKey('workflow_steps.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'running', 'completed', 'failed', 'skipped'
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    
    # Relationships
    workflow_step = db.relationship('WorkflowStep', backref='executions')
    
    def __repr__(self):
        return f'<StepExecution {self.id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'workflow_execution_id': self.workflow_execution_id,
            'workflow_step_id': self.workflow_step_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'duration': (self.completed_at - self.started_at).total_seconds() if self.completed_at and self.started_at else None
        }

