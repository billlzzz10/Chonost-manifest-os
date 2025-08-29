"""
📱 Mobile Assistant API Endpoints
API endpoints สำหรับ Mobile Assistant ที่รวมเข้ากับ Chonost
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
from mobile_assistant_core import ChonostMobileIntegration

app = Flask(__name__)
CORS(app)

# สร้าง instance ของ Mobile Assistant
mobile_integration = ChonostMobileIntegration()


@app.route('/api/mobile/chat', methods=['POST'])
def chat():
    """API endpoint สำหรับการสนทนา"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({"error": "ข้อความไม่สามารถเป็นค่าว่างได้"}), 400
        
        # เรียกใช้ async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            mobile_integration.process_request(user_id, message, conversation_id)
        )
        loop.close()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": f"เกิดข้อผิดพลาด: {str(e)}"}), 500


@app.route('/api/mobile/conversations/<user_id>', methods=['GET'])
def get_conversations(user_id):
    """ดึงการสนทนาของผู้ใช้"""
    try:
        # จำลองการดึงการสนทนา
        conversations = [
            {
                "id": "conv_1",
                "title": "การสนทนาล่าสุด",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        return jsonify({"conversations": conversations})
        
    except Exception as e:
        return jsonify({"error": f"เกิดข้อผิดพลาด: {str(e)}"}), 500


@app.route('/api/mobile/conversation/<conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """ดึงข้อความในการสนทนา"""
    try:
        # จำลองการดึงข้อความ
        messages = [
            {
                "id": "msg_1",
                "user_id": "user_123",
                "content": "สวัสดีครับ",
                "timestamp": datetime.now().isoformat(),
                "intent": {"type": "greeting", "confidence": 0.9},
                "response": "สวัสดีครับ! ยินดีต้อนรับสู่ Chonost Mobile Assistant"
            }
        ]
        
        return jsonify({"messages": messages})
        
    except Exception as e:
        return jsonify({"error": f"เกิดข้อผิดพลาด: {str(e)}"}), 500


@app.route('/api/mobile/conversation/<conversation_id>/summary', methods=['GET'])
def get_conversation_summary(conversation_id):
    """ดึงสรุปการสนทนา"""
    try:
        # จำลองการสรุปการสนทนา
        summary = {
            "conversation_id": conversation_id,
            "title": "การสนทนาล่าสุด",
            "total_messages": 5,
            "user_messages": 3,
            "assistant_messages": 2,
            "intent_distribution": {
                "greeting": 1,
                "question": 2
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({"error": f"เกิดข้อผิดพลาด: {str(e)}"}), 500


@app.route('/api/mobile/health', methods=['GET'])
def health_check():
    """ตรวจสอบสถานะระบบ"""
    return jsonify({
        "status": "healthy",
        "service": "Mobile Assistant",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
