
"""
Chat Integration Backend Application

This module provides the Flask application factory for the Chat Integration Backend.
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restx import Api
from src.models.user import db
from src.models.chat import ChatSession, Message
from src.models.automation import Workflow, WorkflowExecution, ServiceConnection, AutomationTemplate
from src.routes.user import user_bp
from src.routes.chat_routes import chat_bp
from src.routes.automation_routes import automation_bp
from src.routes.file_routes import file_bp, api as file_api
from src.routes.agent_routes import agent_bp
from src.routes.health import health_bp


def create_app(config=None):
    """Create and configure the Flask application.
    
    Args:
        config (dict, optional): Configuration dictionary to override defaults.
        
    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Default configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Override with custom config if provided
    if config:
        app.config.update(config)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(automation_bp, url_prefix='/api')
    app.register_blueprint(file_bp, url_prefix='/api')
    app.register_blueprint(agent_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create necessary directories
        os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), 'uploads'), exist_ok=True)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Serve static files and handle SPA routing."""
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    return app


def create_test_app():
    """Create a Flask application configured for testing.
    
    Returns:
        Flask: Flask application instance configured for testing.
    """
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    }
    return create_app(test_config)

