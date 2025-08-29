from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.services.ai_service import AIService
import json

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()

@ai_bp.route('/ai/analyze-characters', methods=['POST'])
@cross_origin()
def analyze_characters():
    """
    วิเคราะห์ตัวละครจากเนื้อหา
    """
    try:
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        result = ai_service.analyze_characters(content)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/writing-assistant', methods=['POST'])
@cross_origin()
def writing_assistant():
    """
    ผู้ช่วยการเขียน
    """
    try:
        data = request.json
        content = data.get('content', '')
        request_type = data.get('type', 'improve')  # improve, continue, suggest, grammar
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        result = ai_service.writing_assistant(content, request_type)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/auto-complete', methods=['POST'])
@cross_origin()
def auto_complete():
    """
    Auto-completion สำหรับการเขียน
    """
    try:
        data = request.json
        content = data.get('content', '')
        cursor_position = data.get('cursor_position')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        result = ai_service.auto_complete(content, cursor_position)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/enhance-content', methods=['POST'])
@cross_origin()
def enhance_content():
    """
    ปรับปรุงเนื้อหาด้วย AI
    """
    try:
        data = request.json
        content = data.get('content', '')
        enhancement_type = data.get('type', 'general')  # general, dialogue, description, pacing, emotion
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        result = ai_service.enhance_content(content, enhancement_type)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/models', methods=['GET'])
@cross_origin()
def get_available_models():
    """
    ดึงรายการ AI models ที่ใช้งานได้
    """
    try:
        models_info = {
            'character_analysis': {
                'model': ai_service.models['character_analysis'],
                'description': 'วิเคราะห์ตัวละครและความสัมพันธ์',
                'capabilities': ['character_detection', 'personality_analysis', 'relationship_mapping']
            },
            'writing_assistant': {
                'model': ai_service.models['writing_assistant'],
                'description': 'ผู้ช่วยการเขียนและให้คำแนะนำ',
                'capabilities': ['content_improvement', 'story_continuation', 'writing_suggestions', 'grammar_check']
            },
            'auto_completion': {
                'model': ai_service.models['auto_completion'],
                'description': 'เติมข้อความอัตโนมัติ',
                'capabilities': ['text_completion', 'context_aware_suggestions']
            },
            'content_enhancement': {
                'model': ai_service.models['content_enhancement'],
                'description': 'ปรับปรุงเนื้อหาขั้นสูง',
                'capabilities': ['dialogue_enhancement', 'description_improvement', 'pacing_adjustment', 'emotional_depth']
            }
        }
        
        return jsonify({
            'success': True,
            'models': models_info,
            'total_models': len(models_info)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/health', methods=['GET'])
@cross_origin()
def ai_health_check():
    """
    ตรวจสอบสถานะของ AI Service
    """
    try:
        # ทดสอบการเชื่อมต่อกับ OpenAI API
        test_result = ai_service.auto_complete("Hello", 5)
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'api_connection': test_result.get('success', False),
            'available_models': list(ai_service.models.keys())
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

