from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.automation import Workflow, WorkflowExecution, ServiceConnection, AutomationTemplate
from datetime import datetime

automation_bp = Blueprint('automation', __name__)

# Workflow routes
@automation_bp.route('/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows for a user"""
    try:
        user_id = request.args.get('user_id', 1)
        
        workflows = Workflow.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(Workflow.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [workflow.to_dict() for workflow in workflows]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow"""
    try:
        data = request.get_json()
        
        workflow = Workflow(
            user_id=data.get('user_id', 1),
            name=data['name'],
            description=data.get('description', ''),
            trigger_config=data.get('trigger_config', {}),
            steps_config=data.get('steps_config', [])
        )
        
        db.session.add(workflow)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': workflow.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/workflows/<int:workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get a specific workflow"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        return jsonify({
            'success': True,
            'data': workflow.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/workflows/<int:workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    """Update a workflow"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        data = request.get_json()
        
        if 'name' in data:
            workflow.name = data['name']
        if 'description' in data:
            workflow.description = data['description']
        if 'is_active' in data:
            workflow.is_active = data['is_active']
        if 'trigger_config' in data:
            workflow.trigger_config = data['trigger_config']
        if 'steps_config' in data:
            workflow.steps_config = data['steps_config']
        
        workflow.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': workflow.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/workflows/<int:workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    """Delete a workflow"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        workflow.is_active = False
        workflow.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Workflow deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/workflows/<int:workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """Execute a workflow"""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        data = request.get_json()
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status='pending',
            execution_data=data.get('input_data', {})
        )
        
        db.session.add(execution)
        db.session.commit()
        
        # TODO: Implement actual workflow execution logic
        # For now, just mark as completed
        execution.status = 'completed'
        execution.completed_at = datetime.utcnow()
        execution.execution_data['result'] = 'Workflow executed successfully (mock)'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': execution.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Service Connection routes
@automation_bp.route('/connections', methods=['GET'])
def get_connections():
    """Get all service connections for a user"""
    try:
        user_id = request.args.get('user_id', 1)
        
        connections = ServiceConnection.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(ServiceConnection.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [connection.to_dict() for connection in connections]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/connections', methods=['POST'])
def create_connection():
    """Create a new service connection"""
    try:
        data = request.get_json()
        
        connection = ServiceConnection(
            user_id=data.get('user_id', 1),
            service_name=data['service_name'],
            connection_name=data['connection_name'],
            config=data.get('config', {})
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': connection.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/connections/<int:connection_id>', methods=['PUT'])
def update_connection(connection_id):
    """Update a service connection"""
    try:
        connection = ServiceConnection.query.get_or_404(connection_id)
        data = request.get_json()
        
        if 'connection_name' in data:
            connection.connection_name = data['connection_name']
        if 'is_active' in data:
            connection.is_active = data['is_active']
        if 'config' in data:
            connection.config = data['config']
        
        connection.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': connection.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/connections/<int:connection_id>', methods=['DELETE'])
def delete_connection(connection_id):
    """Delete a service connection"""
    try:
        connection = ServiceConnection.query.get_or_404(connection_id)
        connection.is_active = False
        connection.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Connection deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Automation Template routes
@automation_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all automation templates"""
    try:
        category = request.args.get('category')
        complexity = request.args.get('complexity')
        
        query = AutomationTemplate.query.filter_by(is_public=True)
        
        if category:
            query = query.filter_by(category=category)
        if complexity:
            query = query.filter_by(complexity=complexity)
        
        templates = query.order_by(AutomationTemplate.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new automation template"""
    try:
        data = request.get_json()
        
        template = AutomationTemplate(
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            complexity=data.get('complexity', 'medium'),
            services=data.get('services', []),
            template_config=data.get('template_config', {}),
            is_public=data.get('is_public', True)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': template.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/templates/<int:template_id>/create-workflow', methods=['POST'])
def create_workflow_from_template(template_id):
    """Create a workflow from a template"""
    try:
        template = AutomationTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        workflow = Workflow(
            user_id=data.get('user_id', 1),
            name=data.get('name', template.name),
            description=template.description,
            trigger_config=template.template_config.get('trigger', {}),
            steps_config=template.template_config.get('steps', [])
        )
        
        db.session.add(workflow)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': workflow.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

