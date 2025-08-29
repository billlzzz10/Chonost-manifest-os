"""
Health Check Routes

This module provides health check endpoints for monitoring and load balancing.
"""

from flask import Blueprint, jsonify
from src.database import get_db_connection
import time
import os

health_bp = Blueprint("health", __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint
    Returns 200 if the service is running
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'chat-backend',
        'version': '1.0.0'
    }), 200

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check that tests database connectivity
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'chat-backend',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Check database connectivity
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            if result and result[0] == 1:
                health_status['checks']['database'] = {
                    'status': 'healthy',
                    'message': 'Database connection successful'
                }
            else:
                health_status['checks']['database'] = {
                    'status': 'unhealthy',
                    'message': 'Database query failed'
                }
                health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Check disk space
    try:
        disk_usage = os.statvfs('/')
        free_space = disk_usage.f_bavail * disk_usage.f_frsize
        total_space = disk_usage.f_blocks * disk_usage.f_frsize
        used_percentage = ((total_space - free_space) / total_space) * 100
        
        if used_percentage < 90:
            health_status['checks']['disk_space'] = {
                'status': 'healthy',
                'used_percentage': round(used_percentage, 2),
                'message': 'Disk space is adequate'
            }
        else:
            health_status['checks']['disk_space'] = {
                'status': 'warning',
                'used_percentage': round(used_percentage, 2),
                'message': 'Disk space is running low'
            }
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'unknown',
            'message': f'Could not check disk space: {str(e)}'
        }
    
    # Check environment variables
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if not missing_vars:
        health_status['checks']['environment'] = {
            'status': 'healthy',
            'message': 'All required environment variables are set'
        }
    else:
        health_status['checks']['environment'] = {
            'status': 'unhealthy',
            'message': f'Missing environment variables: {", ".join(missing_vars)}'
        }
        health_status['status'] = 'unhealthy'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration
    """
    try:
        # Test database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
        
        return jsonify({
            'status': 'ready',
            'timestamp': time.time()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration
    """
    return jsonify({
        'status': 'alive',
        'timestamp': time.time()
    }), 200

