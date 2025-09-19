"""
🎯 Integrated Routes for Chonost System
Routes ที่ผนวกรวมทุกฟีเจอร์เข้าด้วยกัน
"""
from fastapi import APIRouter, Query, Body
from fastapi.responses import JSONResponse
import json
import asyncio
import sqlite3
import re
from datetime import datetime
from typing import Dict, Any, Optional
from src.integrated_system_core import (
    get_integrated_system,
    Task,
    AgentType,
    TaskPriority,
    TaskStatus,
)

# FastAPI router (ใช้ prefix "/integrated")
intergrated_router = APIRouter(prefix="/integrated", tags=["integrated"])
# Alias ที่สะกดถูกต้อง (เผื่อโค้ดภายนอกอ้างอิง)
integrated_router = intergrated_router

system = get_integrated_system()

@intergrated_router.get("/manuscripts")
def get_manuscripts(user_id: str = Query("default_user")):
    """ดึงรายการ manuscripts ทั้งหมด"""
    try:
        # Input validation
        if not user_id or not isinstance(user_id, str):
            return JSONResponse({
                'success': False,
                'error': 'Invalid user_id parameter'
            }, status_code=400)
        
        # Sanitize user_id
        user_id = re.sub(r'[^a-zA-Z0-9_-]', '', user_id)
        if not user_id:
            return JSONResponse({
                'success': False,
                'error': 'Invalid user_id format'
            }, status_code=400)
        
        manuscripts = system.get_user_manuscripts(user_id)
        
        return {
            'success': True,
            'manuscripts': manuscripts,
            'total': len(manuscripts)
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/manuscripts")
def create_manuscript(data: Optional[Dict[str, Any]] = Body(None)):
    """สร้าง manuscript ใหม่"""
    try:
        if not data:
            return JSONResponse({'success': False, 'error': 'Request body is required'}, status_code=400)
        
        user_id = data.get('user_id', 'default_user')
        title = data.get('title', 'Untitled')
        content = data.get('content', '')
        
        # Input validation
        if not isinstance(user_id, str) or not isinstance(title, str) or not isinstance(content, str):
            return JSONResponse({'success': False, 'error': 'Invalid data types'}, status_code=400)
        
        # Sanitize inputs
        user_id = re.sub(r'[^a-zA-Z0-9_-]', '', user_id)
        title = title.strip()[:200]  # Limit title length
        content = content.strip()[:50000]  # Limit content length
        
        if not user_id:
            return JSONResponse({'success': False, 'error': 'Invalid user_id format'}, status_code=400)
        
        manuscript_id = system.create_manuscript(user_id, title, content)
        
        return {
            'success': True,
            'manuscript_id': manuscript_id,
            'message': 'Manuscript created successfully'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.get("/manuscripts/{manuscript_id}")
def get_manuscript(manuscript_id: str):
    """ดึง manuscript ตาม ID"""
    try:
        manuscript = system.get_manuscript(manuscript_id)
        if not manuscript:
            return JSONResponse({'success': False, 'error': 'Manuscript not found'}, status_code=404)
        
        return {
            'success': True,
            'manuscript': manuscript
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.put("/manuscripts/{manuscript_id}")
def update_manuscript(manuscript_id: str, data: Optional[Dict[str, Any]] = Body(None)):
    """อัปเดต manuscript"""
    try:
        content = (data or {}).get('content', '')
        
        success = system.update_manuscript(manuscript_id, content)
        if not success:
            return JSONResponse({'success': False, 'error': 'Failed to update manuscript'}, status_code=500)
        
        return {
            'success': True,
            'message': 'Manuscript updated successfully'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/ai/analyze-characters")
async def analyze_characters(data: Optional[Dict[str, Any]] = Body(None)):
    """วิเคราะห์ตัวละครจากเนื้อหา"""
    try:
        content = (data or {}).get('content', '')
        
        if not content:
            return JSONResponse({'error': 'Content is required'}, status_code=400)
        
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
        try:
            await system.submit_task(task)
        except Exception as task_error:
            return JSONResponse({'success': False, 'error': f'Failed to submit task: {str(task_error)}'}, status_code=500)
        
        return {
            'success': True,
            'task_id': task.id,
            'message': 'Character analysis task submitted'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/ai/analyze-plot")
async def analyze_plot(data: Optional[Dict[str, Any]] = Body(None)):
    """วิเคราะห์โครงเรื่อง"""
    try:
        content = (data or {}).get('content', '')
        
        if not content:
            return JSONResponse({'error': 'Content is required'}, status_code=400)
        
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
        try:
            await system.submit_task(task)
        except Exception as task_error:
            return JSONResponse({'success': False, 'error': f'Failed to submit task: {str(task_error)}'}, status_code=500)
        
        return {
            'success': True,
            'task_id': task.id,
            'message': 'Plot analysis task submitted'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/ai/writing-assistant")
async def writing_assistant(data: Optional[Dict[str, Any]] = Body(None)):
    """ผู้ช่วยการเขียน"""
    try:
        content = (data or {}).get('content', '')
        request_type = (data or {}).get('type', 'improve')
        
        if not content:
            return JSONResponse({'error': 'Content is required'}, status_code=400)
        
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
        try:
            await system.submit_task(task)
        except Exception as task_error:
            return JSONResponse({'success': False, 'error': f'Failed to submit task: {str(task_error)}'}, status_code=500)
        
        return {
            'success': True,
            'task_id': task.id,
            'message': 'Writing assistant task submitted'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/ai/inline-editor")
async def inline_editor(data: Optional[Dict[str, Any]] = Body(None)):
    """Inline Editor สำหรับแก้ไขเนื้อหา"""
    try:
        content = (data or {}).get('content', '')
        action = (data or {}).get('action', 'improve')
        
        if not content:
            return JSONResponse({'error': 'Content is required'}, status_code=400)
        
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
        try:
            await system.submit_task(task)
        except Exception as task_error:
            return JSONResponse({'success': False, 'error': f'Failed to submit task: {str(task_error)}'}, status_code=500)
        
        return {
            'success': True,
            'task_id': task.id,
            'message': 'Inline editor task submitted'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/ai/assistant-chat")
async def assistant_chat(data: Optional[Dict[str, Any]] = Body(None)):
    """Assistant Chat สำหรับคำถามเชิงลึก"""
    try:
        question = (data or {}).get('question', '')
        user_id = (data or {}).get('user_id', 'default_user')
        
        if not question:
            return JSONResponse({'error': 'Question is required'}, status_code=400)
        
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
        try:
            await system.submit_task(task)
        except Exception as task_error:
            return JSONResponse({'success': False, 'error': f'Failed to submit task: {str(task_error)}'}, status_code=500)
        
        return {
            'success': True,
            'task_id': task.id,
            'message': 'Assistant chat task submitted'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/ai/rag-search")
async def rag_search(data: Optional[Dict[str, Any]] = Body(None)):
    """ค้นหาด้วย RAG system"""
    try:
        query = (data or {}).get('query', '')
        
        if not query:
            return JSONResponse({'error': 'Query is required'}, status_code=400)
        
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
        try:
            await system.submit_task(task)
        except Exception as task_error:
            return JSONResponse({'success': False, 'error': f'Failed to submit task: {str(task_error)}'}, status_code=500)
        
        return {
            'success': True,
            'task_id': task.id,
            'message': 'RAG search task submitted'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """ดึงสถานะของ task"""
    try:
        task_status = await system.get_task_status(task_id)
        
        if not task_status:
            return JSONResponse({'success': False, 'error': 'Task not found'}, status_code=404)
        
        return {
            'success': True,
            'task': task_status
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.get("/tasks")
def get_all_tasks():
    """ดึงรายการ tasks ทั้งหมด"""
    try:
        # ดึงจากฐานข้อมูล (ใช้ parameterized query)
        conn = sqlite3.connect(system.db_path)
        cursor = conn.cursor()
        
        # ใช้ parameterized query เพื่อป้องกัน SQL injection
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?', (50,))
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
        
        return {
            'success': True,
            'tasks': tasks,
            'total': len(tasks)
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.get("/analytics/overview")
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
        
        # นับจำนวน tasks ที่เสร็จแล้ว (ใช้ parameterized query)
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = ?', ('completed',))
        completed_tasks = cursor.fetchone()[0]
        
        # นับจำนวน characters
        cursor.execute('SELECT COUNT(*) FROM characters')
        character_count = cursor.fetchone()[0]
        
        # คำนวณ success rate
        success_rate = (completed_tasks / task_count * 100) if task_count > 0 else 0
        
        conn.close()
        
        return {
            'success': True,
            'analytics': {
                'manuscript_count': manuscript_count,
                'task_count': task_count,
                'completed_tasks': completed_tasks,
                'character_count': character_count,
                'success_rate': round(success_rate, 2)
            }
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.post("/feedback")
def submit_feedback(data: Optional[Dict[str, Any]] = Body(None)):
    """ส่ง feedback"""
    try:
        data = data or {}
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
        
        return {
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback submitted successfully'
        }
    except Exception as e:
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@intergrated_router.get("/system/health")
def system_health():
    """ตรวจสอบสถานะระบบ"""
    try:
        # ตรวจสอบการเชื่อมต่อฐานข้อมูล
        try:
            conn = sqlite3.connect(system.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            db_healthy = cursor.fetchone() is not None
            conn.close()
        except Exception as db_error:
            db_healthy = False
            print(f"Database health check failed: {db_error}")
        
        # ตรวจสอบ embedding model
        embedding_healthy = system.embedding_model is not None
        
        # ตรวจสอบ vector store
        vector_store_healthy = system.vector_store is not None
        
        # ตรวจสอบ OpenAI API
        try:
            openai_healthy = system.openai_client.api_key is not None and len(system.openai_client.api_key) > 0
        except Exception as openai_error:
            openai_healthy = False
            print(f"OpenAI API health check failed: {openai_error}")
        
        overall_health = all([db_healthy, embedding_healthy, vector_store_healthy, openai_healthy])
        
        return {
            'success': True,
            'health': {
                'overall': 'healthy' if overall_health else 'unhealthy',
                'database': 'healthy' if db_healthy else 'unhealthy',
                'embedding_model': 'healthy' if embedding_healthy else 'unhealthy',
                'vector_store': 'healthy' if vector_store_healthy else 'unhealthy',
                'openai_api': 'healthy' if openai_healthy else 'unhealthy'
            }
        }
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e),
            'health': {
                'overall': 'unhealthy',
                'error': str(e)
            }
        }, status_code=500)
