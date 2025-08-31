"""
🎯 Integrated Routes for Chonost System
Routes ที่ผนวกรวมทุกฟีเจอร์เข้าด้วยกัน
"""
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import json
import asyncio
from datetime import datetime
from src.integrated_system_core import get_integrated_system, Task, AgentType, TaskPriority, TaskStatus

integrated_bp = Blueprint('integrated', __name__)
system = get_integrated_system()

@integrated_bp.route('/integrated/manuscripts', methods=['GET'])
@cross_origin()
def get_manuscripts():
    """ดึงรายการ manuscripts ทั้งหมด"""
    try:
        # ดึงจากระบบ integrated
        user_id = request.args.get('user_id', 'default_user')
        manuscripts = system.get_user_manuscripts(user_id)
        
        return jsonify({
            'success': True,
            'manuscripts': manuscripts,
            'total': len(manuscripts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/manuscripts', methods=['POST'])
@cross_origin()
def create_manuscript():
    """สร้าง manuscript ใหม่"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        title = data.get('title', 'Untitled')
        content = data.get('content', '')
        
        manuscript_id = system.create_manuscript(user_id, title, content)
        
        return jsonify({
            'success': True,
            'manuscript_id': manuscript_id,
            'message': 'Manuscript created successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/manuscripts/<manuscript_id>', methods=['GET'])
@cross_origin()
def get_manuscript(manuscript_id):
    """ดึง manuscript ตาม ID"""
    try:
        manuscript = system.get_manuscript(manuscript_id)
        if not manuscript:
            return jsonify({
                'success': False,
                'error': 'Manuscript not found'
            }), 404
        
        return jsonify({
            'success': True,
            'manuscript': manuscript
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/manuscripts/<manuscript_id>', methods=['PUT'])
@cross_origin()
def update_manuscript(manuscript_id):
    """อัปเดต manuscript"""
    try:
        data = request.json
        content = data.get('content', '')
        
        success = system.update_manuscript(manuscript_id, content)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update manuscript'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Manuscript updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/ai/analyze-characters', methods=['POST'])
@cross_origin()
def analyze_characters():
    """วิเคราะห์ตัวละครจากเนื้อหา"""
    try:
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # สร้าง task สำหรับ character analysis
        task = Task(
            id=f"char_analysis_{int(datetime.now().timestamp())}",
            title="Character Analysis",
            description="Analyze characters from content",
            agent_type=AgentType.CHARACTER_ANALYZER,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"content": content}
        )
        
        # ส่ง task ไปประมวลผล
        asyncio.create_task(system.submit_task(task))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Character analysis task submitted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/ai/analyze-plot', methods=['POST'])
@cross_origin()
def analyze_plot():
    """วิเคราะห์โครงเรื่อง"""
    try:
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # สร้าง task สำหรับ plot analysis
        task = Task(
            id=f"plot_analysis_{int(datetime.now().timestamp())}",
            title="Plot Analysis",
            description="Analyze plot structure and themes",
            agent_type=AgentType.PLOT_ANALYZER,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"content": content}
        )
        
        # ส่ง task ไปประมวลผล
        asyncio.create_task(system.submit_task(task))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Plot analysis task submitted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/ai/writing-assistant', methods=['POST'])
@cross_origin()
def writing_assistant():
    """ผู้ช่วยการเขียน"""
    try:
        data = request.json
        content = data.get('content', '')
        request_type = data.get('type', 'improve')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # สร้าง task สำหรับ writing assistant
        task = Task(
            id=f"writing_assistant_{int(datetime.now().timestamp())}",
            title="Writing Assistant",
            description="Provide writing assistance",
            agent_type=AgentType.WRITING_ASSISTANT,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"content": content, "type": request_type}
        )
        
        # ส่ง task ไปประมวลผล
        asyncio.create_task(system.submit_task(task))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Writing assistant task submitted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/ai/inline-editor', methods=['POST'])
@cross_origin()
def inline_editor():
    """Inline Editor สำหรับแก้ไขเนื้อหา"""
    try:
        data = request.json
        content = data.get('content', '')
        action = data.get('action', 'improve')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # สร้าง task สำหรับ inline editor
        task = Task(
            id=f"inline_editor_{int(datetime.now().timestamp())}",
            title="Inline Editor",
            description="Process inline editing request",
            agent_type=AgentType.INLINE_EDITOR,
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"content": content, "action": action}
        )
        
        # ส่ง task ไปประมวลผล
        asyncio.create_task(system.submit_task(task))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Inline editor task submitted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/ai/assistant-chat', methods=['POST'])
@cross_origin()
def assistant_chat():
    """Assistant Chat สำหรับคำถามเชิงลึก"""
    try:
        data = request.json
        question = data.get('question', '')
        user_id = data.get('user_id', 'default_user')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # สร้าง task สำหรับ assistant chat
        task = Task(
            id=f"assistant_chat_{int(datetime.now().timestamp())}",
            title="Assistant Chat",
            description="Process deep analysis question",
            agent_type=AgentType.ASSISTANT_CHAT,
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"question": question, "user_id": user_id}
        )
        
        # ส่ง task ไปประมวลผล
        asyncio.create_task(system.submit_task(task))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Assistant chat task submitted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/ai/rag-search', methods=['POST'])
@cross_origin()
def rag_search():
    """ค้นหาด้วย RAG system"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # สร้าง task สำหรับ RAG search
        task = Task(
            id=f"rag_search_{int(datetime.now().timestamp())}",
            title="RAG Search",
            description="Search using RAG system",
            agent_type=AgentType.RAG_ENGINE,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"query": query}
        )
        
        # ส่ง task ไปประมวลผล
        asyncio.create_task(system.submit_task(task))
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'RAG search task submitted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/tasks/<task_id>', methods=['GET'])
@cross_origin()
def get_task_status(task_id):
    """ดึงสถานะของ task"""
    try:
        task_status = asyncio.run(system.get_task_status(task_id))
        
        if not task_status:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        return jsonify({
            'success': True,
            'task': task_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/tasks', methods=['GET'])
@cross_origin()
def get_all_tasks():
    """ดึงรายการ tasks ทั้งหมด"""
    try:
        # ดึงจากฐานข้อมูล
        conn = system.db_path
        import sqlite3
        conn = sqlite3.connect(conn)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC LIMIT 50')
        rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            tasks.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "agent_type": row[3],
                "priority": row[4],
                "status": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "result": json.loads(row[10]) if row[10] else None
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total': len(tasks)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/analytics/overview', methods=['GET'])
@cross_origin()
def get_analytics_overview():
    """ดึงภาพรวม analytics"""
    try:
        # ดึงข้อมูลสถิติ
        conn = sqlite3.connect(system.db_path)
        cursor = conn.cursor()
        
        # นับจำนวน manuscripts
        cursor.execute('SELECT COUNT(*) FROM manuscripts')
        manuscript_count = cursor.fetchone()[0]
        
        # นับจำนวน tasks
        cursor.execute('SELECT COUNT(*) FROM tasks')
        task_count = cursor.fetchone()[0]
        
        # นับจำนวน tasks ที่เสร็จแล้ว
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed_tasks = cursor.fetchone()[0]
        
        # นับจำนวน characters
        cursor.execute('SELECT COUNT(*) FROM characters')
        character_count = cursor.fetchone()[0]
        
        # คำนวณ success rate
        success_rate = (completed_tasks / task_count * 100) if task_count > 0 else 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'analytics': {
                'manuscript_count': manuscript_count,
                'task_count': task_count,
                'completed_tasks': completed_tasks,
                'character_count': character_count,
                'success_rate': round(success_rate, 2)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/feedback', methods=['POST'])
@cross_origin()
def submit_feedback():
    """ส่ง feedback"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        content_type = data.get('content_type', 'manuscript')
        content_id = data.get('content_id', '')
        feedback_type = data.get('feedback_type', 'general')
        feedback_data = data.get('feedback_data', {})
        
        # บันทึก feedback
        conn = sqlite3.connect(system.db_path)
        cursor = conn.cursor()
        
        feedback_id = f"feedback_{int(datetime.now().timestamp())}"
        cursor.execute('''
            INSERT INTO feedback (id, user_id, content_type, content_id, feedback_type, feedback_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (feedback_id, user_id, content_type, content_id, feedback_type, json.dumps(feedback_data)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback submitted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrated_bp.route('/integrated/system/health', methods=['GET'])
@cross_origin()
def system_health():
    """ตรวจสอบสถานะระบบ"""
    try:
        # ตรวจสอบการเชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect(system.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        db_healthy = cursor.fetchone() is not None
        conn.close()
        
        # ตรวจสอบ embedding model
        embedding_healthy = system.embedding_model is not None
        
        # ตรวจสอบ vector store
        vector_store_healthy = system.vector_store is not None
        
        # ตรวจสอบ OpenAI API
        openai_healthy = system.openai_client.api_key is not None
        
        overall_health = all([db_healthy, embedding_healthy, vector_store_healthy, openai_healthy])
        
        return jsonify({
            'success': True,
            'health': {
                'overall': 'healthy' if overall_health else 'unhealthy',
                'database': 'healthy' if db_healthy else 'unhealthy',
                'embedding_model': 'healthy' if embedding_healthy else 'unhealthy',
                'vector_store': 'healthy' if vector_store_healthy else 'unhealthy',
                'openai_api': 'healthy' if openai_healthy else 'unhealthy'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'health': {
                'overall': 'unhealthy',
                'error': str(e)
            }
        }), 500
