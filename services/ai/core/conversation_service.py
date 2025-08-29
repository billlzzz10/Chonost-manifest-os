"""
📱 Mobile Assistant Core System
ระบบหลักสำหรับ Mobile Assistant ที่รวมเข้ากับ Chonost
"""
import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntentType(Enum):
    GREETING = "greeting"
    QUESTION = "question"
    TASK_REQUEST = "task_request"
    SYSTEM_COMMAND = "system_command"
    CHAT = "chat"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    type: IntentType
    confidence: float
    entities: Dict[str, Any] = None
    context: Dict[str, Any] = None


@dataclass
class Message:
    id: str
    user_id: str
    content: str
    timestamp: datetime
    intent: Optional[Intent] = None
    response: Optional[str] = None


class IntentDetectionSystem:
    """ระบบตรวจจับ Intent"""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.GREETING: ["hello", "hi", "hey", "สวัสดี", "หวัดดี"],
            IntentType.QUESTION: ["what", "how", "why", "อะไร", "อย่างไร", "ทำไม"],
            IntentType.TASK_REQUEST: ["create", "make", "build", "สร้าง", "ทำ"],
            IntentType.SYSTEM_COMMAND: ["stop", "status", "help", "หยุด", "สถานะ"],
            IntentType.HELP: ["help", "support", "ช่วยเหลือ", "คู่มือ"]
        }
    
    async def detect_intent(self, message: str) -> Intent:
        """ตรวจจับ Intent จากข้อความ"""
        message_lower = message.lower()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    confidence = len(pattern) / len(message_lower)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type
        
        return Intent(type=best_intent, confidence=best_confidence)


class ConversationService:
    """บริการจัดการการสนทนา"""
    
    def __init__(self, db_path: str = "mobile_assistant.db"):
        self.db_path = db_path
        self.intent_detector = IntentDetectionSystem()
        self._init_database()
    
    def _init_database(self):
        """เริ่มต้นฐานข้อมูล"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    intent_type TEXT,
                    intent_confidence REAL,
                    response TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            conn.commit()
    
    async def create_conversation(self, user_id: str, title: str = None) -> str:
        """สร้างการสนทนาใหม่"""
        import uuid
        conversation_id = str(uuid.uuid4())
        title = title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                conversation_id, user_id, title,
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            conn.commit()
        
        return conversation_id
    
    async def send_message(self, conversation_id: str, user_id: str, content: str) -> Message:
        """ส่งข้อความ"""
        import uuid
        
        # ตรวจจับ Intent
        intent = await self.intent_detector.detect_intent(content)
        
        # สร้างการตอบสนอง
        response = await self._generate_response(intent, content)
        
        # สร้างข้อความ
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            user_id=user_id,
            content=content,
            timestamp=datetime.now(),
            intent=intent,
            response=response
        )
        
        # บันทึกลงฐานข้อมูล
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages 
                (id, conversation_id, user_id, content, timestamp, intent_type, intent_confidence, response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.id, conversation_id, message.user_id, message.content,
                message.timestamp.isoformat(), message.intent.type.value,
                message.intent.confidence, message.response
            ))
            conn.commit()
        
        return message
    
    async def _generate_response(self, intent: Intent, content: str) -> str:
        """สร้างการตอบสนอง"""
        if intent.type == IntentType.GREETING:
            return "สวัสดีครับ! ยินดีต้อนรับสู่ Chonost Mobile Assistant"
        
        elif intent.type == IntentType.QUESTION:
            return f"เกี่ยวกับคำถามของคุณ: '{content}'\n\nผมกำลังค้นหาข้อมูลที่เกี่ยวข้อง..."
        
        elif intent.type == IntentType.TASK_REQUEST:
            return f"เข้าใจแล้วครับ คุณต้องการ: {content}\n\nกำลังประมวลผลงาน..."
        
        elif intent.type == IntentType.SYSTEM_COMMAND:
            return "คำสั่งระบบได้รับการประมวลผลเรียบร้อยแล้ว"
        
        elif intent.type == IntentType.HELP:
            return "🤖 **คู่มือการใช้งาน**\n\n- สนทนาธรรมดา\n- ถามข้อมูลต่างๆ\n- สร้างและจัดการงาน\n- คำสั่งระบบ"
        
        else:
            return "เข้าใจแล้วครับ มีอะไรให้ช่วยเหลือเพิ่มเติมไหม?"


class ChonostMobileIntegration:
    """การรวม Mobile Assistant เข้ากับ Chonost"""
    
    def __init__(self):
        self.conversation_service = ConversationService()
    
    async def process_request(self, user_id: str, message: str, conversation_id: str = None) -> Dict[str, Any]:
        """ประมวลผลคำขอจาก Mobile"""
        try:
            # สร้างหรือใช้การสนทนาที่มีอยู่
            if not conversation_id:
                conversation_id = await self.conversation_service.create_conversation(user_id)
            
            # ส่งข้อความ
            message_obj = await self.conversation_service.send_message(conversation_id, user_id, message)
            
            return {
                "conversation_id": conversation_id,
                "message_id": message_obj.id,
                "response": message_obj.response,
                "intent": {
                    "type": message_obj.intent.type.value,
                    "confidence": message_obj.intent.confidence
                },
                "timestamp": message_obj.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {"error": "เกิดข้อผิดพลาดในการประมวลผล"}


# Demo function
async def demo():
    """สาธิตการใช้งาน"""
    print("📱 === Mobile Assistant Demo ===")
    
    integration = ChonostMobileIntegration()
    user_id = "user_123"
    
    # ทดสอบการสนทนา
    messages = [
        "สวัสดีครับ",
        "ช่วยอธิบายเรื่อง AI Agents ให้หน่อย",
        "สร้างงานวิเคราะห์ข้อมูลใหม่",
        "สถานะระบบ"
    ]
    
    conversation_id = None
    
    for message in messages:
        print(f"\nUser: {message}")
        response = await integration.process_request(user_id, message, conversation_id)
        conversation_id = response['conversation_id']
        print(f"Assistant: {response['response']}")
        print(f"Intent: {response['intent']['type']} (confidence: {response['intent']['confidence']:.2f})")


if __name__ == "__main__":
    asyncio.run(demo())
