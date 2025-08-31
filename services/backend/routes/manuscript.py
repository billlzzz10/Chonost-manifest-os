from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json
import os
from datetime import datetime

manuscript_bp = Blueprint('manuscript', __name__)

# ข้อมูลตัวอย่างสำหรับการทดสอบ
sample_manuscripts = [
    {
        'id': 1,
        'title': 'The Chronicles of Aetheria',
        'content': '## บทที่ 1: การเริ่มต้นใหม่\n\nอิกนัส ซิลเวอร์ไนท์ ลืมตาขึ้นมาในความมืดมิดของเหมืองแร่มานา...',
        'characters': ['อิกนัส ซิลเวอร์ไนท์', 'ลิโอซานดร้า', 'เรน่า'],
        'word_count': 1250,
        'created_at': '2025-01-15T10:30:00Z',
        'updated_at': '2025-01-20T14:45:00Z'
    },
    {
        'id': 2,
        'title': 'Modern Romance',
        'content': '## บทที่ 1: การพบกัน\n\nในเมืองใหญ่ที่เต็มไปด้วยผู้คน...',
        'characters': ['อาร์ยา', 'เดวิด', 'มายา'],
        'word_count': 890,
        'created_at': '2025-01-10T09:15:00Z',
        'updated_at': '2025-01-18T16:20:00Z'
    }
]

@manuscript_bp.route('/manuscripts', methods=['GET'])
@cross_origin()
def get_manuscripts():
    """ดึงรายการ manuscripts ทั้งหมด"""
    return jsonify({
        'manuscripts': sample_manuscripts,
        'total': len(sample_manuscripts)
    })

@manuscript_bp.route('/manuscripts/<int:manuscript_id>', methods=['GET'])
@cross_origin()
def get_manuscript(manuscript_id):
    """ดึง manuscript ตาม ID"""
    manuscript = next((m for m in sample_manuscripts if m['id'] == manuscript_id), None)
    if not manuscript:
        return jsonify({'error': 'Manuscript not found'}), 404
    return jsonify(manuscript)

@manuscript_bp.route('/manuscripts', methods=['POST'])
@cross_origin()
def create_manuscript():
    """สร้าง manuscript ใหม่"""
    data = request.json
    new_manuscript = {
        'id': len(sample_manuscripts) + 1,
        'title': data.get('title', 'Untitled'),
        'content': data.get('content', ''),
        'characters': data.get('characters', []),
        'word_count': len(data.get('content', '').split()),
        'created_at': datetime.now().isoformat() + 'Z',
        'updated_at': datetime.now().isoformat() + 'Z'
    }
    sample_manuscripts.append(new_manuscript)
    return jsonify(new_manuscript), 201

@manuscript_bp.route('/manuscripts/<int:manuscript_id>', methods=['PUT'])
@cross_origin()
def update_manuscript(manuscript_id):
    """อัปเดต manuscript"""
    manuscript = next((m for m in sample_manuscripts if m['id'] == manuscript_id), None)
    if not manuscript:
        return jsonify({'error': 'Manuscript not found'}), 404
    
    data = request.json
    manuscript['title'] = data.get('title', manuscript['title'])
    manuscript['content'] = data.get('content', manuscript['content'])
    manuscript['characters'] = data.get('characters', manuscript['characters'])
    manuscript['word_count'] = len(manuscript['content'].split())
    manuscript['updated_at'] = datetime.now().isoformat() + 'Z'
    
    return jsonify(manuscript)

@manuscript_bp.route('/manuscripts/<int:manuscript_id>/analyze', methods=['POST'])
@cross_origin()
def analyze_manuscript(manuscript_id):
    """วิเคราะห์ manuscript (ตัวละคร, โครงเรื่อง, etc.)"""
    manuscript = next((m for m in sample_manuscripts if m['id'] == manuscript_id), None)
    if not manuscript:
        return jsonify({'error': 'Manuscript not found'}), 404
    
    content = manuscript['content']
    
    # การวิเคราะห์เบื้องต้น (จะถูกแทนที่ด้วย AI ในภายหลัง)
    analysis = {
        'word_count': len(content.split()),
        'character_count': len(content),
        'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
        'estimated_reading_time': max(1, len(content.split()) // 200),  # 200 words per minute
        'detected_characters': [],
        'mood': 'neutral',
        'themes': ['adventure', 'fantasy'],
        'writing_style': 'descriptive'
    }
    
    # ตรวจจับชื่อตัวละครแบบง่าย (จะถูกแทนที่ด้วย AI)
    common_thai_names = ['อิกนัส', 'ลิโอซานดร้า', 'เรน่า', 'อาร์ยา', 'เดวิด', 'มายา']
    for name in common_thai_names:
        if name in content:
            analysis['detected_characters'].append(name)
    
    return jsonify(analysis)

@manuscript_bp.route('/manuscripts/<int:manuscript_id>/export', methods=['GET'])
@cross_origin()
def export_manuscript(manuscript_id):
    """ส่งออก manuscript ในรูปแบบต่างๆ"""
    manuscript = next((m for m in sample_manuscripts if m['id'] == manuscript_id), None)
    if not manuscript:
        return jsonify({'error': 'Manuscript not found'}), 404
    
    export_format = request.args.get('format', 'json')
    
    if export_format == 'markdown':
        return manuscript['content'], 200, {'Content-Type': 'text/markdown'}
    elif export_format == 'txt':
        # แปลง markdown เป็น plain text (แบบง่าย)
        plain_text = manuscript['content'].replace('##', '').replace('#', '').strip()
        return plain_text, 200, {'Content-Type': 'text/plain'}
    else:
        return jsonify(manuscript)

