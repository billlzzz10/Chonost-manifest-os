from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.chat import ChatSession, Message
# from src.services.ai_service import ai_service
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions for a user"""
    try:
        user_id = request.args.get('user_id', 1)  # Default to user 1 for now
        
        sessions = ChatSession.query.filter_by(
            user_id=user_id, 
            is_active=True
        ).order_by(ChatSession.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [session.to_dict() for session in sessions]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        title = data.get('title', 'New Chat')
        
        session = ChatSession(
            user_id=user_id,
            title=title
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get a specific chat session with messages"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        
        messages = Message.query.filter_by(
            chat_session_id=session_id
        ).order_by(Message.timestamp.asc()).all()
        
        session_data = session.to_dict()
        session_data['messages'] = [message.to_dict() for message in messages]
        
        return jsonify({
            'success': True,
            'data': session_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['PUT'])
def update_chat_session(session_id):
    """Update a chat session"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        data = request.get_json()
        
        if 'title' in data:
            session.title = data['title']
        
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions/<int:session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        session.is_active = False
        session.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chat session deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions/<int:session_id>/messages', methods=['POST'])
def add_message(session_id):
    """Add a message to a chat session"""
    try:
        session = ChatSession.query.get_or_404(session_id)
        data = request.get_json()
        
        # Add user message
        user_message = Message(
            chat_session_id=session_id,
            content=data['content'],
            role=data.get('role', 'user'),
            message_metadata=data.get('message_metadata', {})
        )
        
        db.session.add(user_message)
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Generate simple AI response (mock)
        if user_message.role == 'user':
            ai_message = Message(
                chat_session_id=session_id,
                content=f"ขอบคุณสำหรับข้อความ: \"{data['content']}\" ฉันเป็น AI Assistant ที่สามารถช่วยคุณเชื่อมต่อและทำงานกับบริการต่างๆ ได้",
                role='assistant',
                message_metadata={}
            )
            
            db.session.add(ai_message)
            session.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'user_message': user_message.to_dict(),
                    'ai_response': ai_message.to_dict()
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': user_message.to_dict()
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/sessions/<int:session_id>/messages', methods=['GET'])
def get_messages(session_id):
    """Get all messages for a chat session"""
    try:
        messages = Message.query.filter_by(
            chat_session_id=session_id
        ).order_by(Message.timestamp.asc()).all()
        
        return jsonify({
            'success': True,
            'data': [message.to_dict() for message in messages]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

