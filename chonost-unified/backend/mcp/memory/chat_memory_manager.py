#!/usr/bin/env python3
"""
Chat Memory Manager
ระบบจัดการ Memory สำหรับการแชตจาก UI

This module provides memory management for chat conversations
โมดูลนี้ให้การจัดการ memory สำหรับการสนทนาในแชต
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """ประเภทของข้อความ"""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    ERROR = "error"
    COMMAND = "command"

class MemoryType(Enum):
    """ประเภทของ Memory"""
    CONVERSATION = "conversation"
    CONTEXT = "context"
    KNOWLEDGE = "knowledge"
    TEMPORARY = "temporary"
    PERSISTENT = "persistent"

@dataclass
class ChatMessage:
    """โครงสร้างข้อมูลสำหรับข้อความในแชต"""
    id: str
    session_id: str
    message_type: MessageType
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    parent_message_id: Optional[str] = None
    response_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "parent_message_id": self.parent_message_id,
            "response_to": self.response_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """สร้างจาก dictionary"""
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data["metadata"],
            parent_message_id=data.get("parent_message_id"),
            response_to=data.get("response_to")
        )

@dataclass
class ChatSession:
    """โครงสร้างข้อมูลสำหรับ session ของแชต"""
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """สร้างจาก dictionary"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            title=data["title"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data["metadata"],
            is_active=data.get("is_active", True)
        )

class ChatMemoryManager:
    """ระบบจัดการ Memory สำหรับการแชต"""
    
    def __init__(self, db_path: str = "data/chat_memory.db"):
        """เริ่มต้น Chat Memory Manager"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Memory cache
        self._session_cache: Dict[str, ChatSession] = {}
        self._message_cache: Dict[str, List[ChatMessage]] = {}
        self._cache_ttl = 3600  # 1 hour
        
        logger.info(f"Chat Memory Manager initialized with database: {self.db_path}")
    
    def _init_database(self):
        """เริ่มต้นฐานข้อมูล"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    parent_message_id TEXT,
                    response_to TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_user ON chat_sessions (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_active ON chat_sessions (is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_session ON chat_messages (session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_message_timestamp ON chat_messages (timestamp)")
            
            conn.commit()
    
    def create_session(self, user_id: str, title: str = "New Chat", metadata: Optional[Dict[str, Any]] = None) -> ChatSession:
        """สร้าง session ใหม่"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at, metadata, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id,
                    session.user_id,
                    session.title,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                    json.dumps(session.metadata),
                    1
                ))
                conn.commit()
            
            # Add to cache
            self._session_cache[session_id] = session
            self._message_cache[session_id] = []
        
        logger.info(f"Created new chat session: {session_id} for user: {user_id}")
        return session
    
    def add_message(self, session_id: str, message_type: MessageType, content: str, 
                   metadata: Optional[Dict[str, Any]] = None, parent_message_id: Optional[str] = None,
                   response_to: Optional[str] = None) -> ChatMessage:
        """เพิ่มข้อความใหม่"""
        message_id = str(uuid.uuid4())
        now = datetime.now()
        
        message = ChatMessage(
            id=message_id,
            session_id=session_id,
            message_type=message_type,
            content=content,
            timestamp=now,
            metadata=metadata or {},
            parent_message_id=parent_message_id,
            response_to=response_to
        )
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_messages (id, session_id, message_type, content, timestamp, metadata, parent_message_id, response_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id,
                    message.session_id,
                    message.message_type.value,
                    message.content,
                    message.timestamp.isoformat(),
                    json.dumps(message.metadata),
                    message.parent_message_id,
                    message.response_to
                ))
                
                # Update session timestamp
                cursor.execute("""
                    UPDATE chat_sessions SET updated_at = ? WHERE id = ?
                """, (now.isoformat(), session_id))
                
                conn.commit()
            
            # Add to cache
            if session_id in self._message_cache:
                self._message_cache[session_id].append(message)
            
            # Update session cache
            if session_id in self._session_cache:
                self._session_cache[session_id].updated_at = now
        
        logger.info(f"Added message to session {session_id}: {message_type.value}")
        return message
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """ดึงข้อมูล session"""
        # Check cache first
        if session_id in self._session_cache:
            return self._session_cache[session_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            
            if row:
                session = ChatSession(
                    id=row[0],
                    user_id=row[1],
                    title=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]),
                    is_active=bool(row[6])
                )
                
                # Add to cache
                self._session_cache[session_id] = session
                return session
        
        return None
    
    def get_messages(self, session_id: str, limit: Optional[int] = None, 
                    offset: int = 0) -> List[ChatMessage]:
        """ดึงข้อความจาก session"""
        # Check cache first
        if session_id in self._message_cache:
            messages = self._message_cache[session_id]
            if limit:
                return messages[offset:offset + limit]
            return messages[offset:]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp"
            params = [session_id]
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = ChatMessage(
                    id=row[0],
                    session_id=row[1],
                    message_type=MessageType(row[2]),
                    content=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]),
                    parent_message_id=row[6],
                    response_to=row[7]
                )
                messages.append(message)
            
            # Add to cache
            self._message_cache[session_id] = messages
            
            return messages
    
    def get_user_sessions(self, user_id: str, limit: Optional[int] = None, 
                         offset: int = 0) -> List[ChatSession]:
        """ดึง sessions ของ user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC"
            params = [user_id]
            
            if limit:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                session = ChatSession(
                    id=row[0],
                    user_id=row[1],
                    title=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]),
                    is_active=bool(row[6])
                )
                sessions.append(session)
            
            return sessions
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """อัปเดตชื่อ session"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chat_sessions SET title = ?, updated_at = ? WHERE id = ?
                """, (title, datetime.now().isoformat(), session_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    
                    # Update cache
                    if session_id in self._session_cache:
                        self._session_cache[session_id].title = title
                        self._session_cache[session_id].updated_at = datetime.now()
                    
                    logger.info(f"Updated session title: {session_id} -> {title}")
                    return True
        
        return False
    
    def deactivate_session(self, session_id: str) -> bool:
        """ปิดใช้งาน session"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chat_sessions SET is_active = 0 WHERE id = ?
                """, (session_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    
                    # Update cache
                    if session_id in self._session_cache:
                        self._session_cache[session_id].is_active = False
                    
                    logger.info(f"Deactivated session: {session_id}")
                    return True
        
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """ลบ session และข้อความทั้งหมด"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first
                cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
                
                # Delete session
                cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    
                    # Remove from cache
                    self._session_cache.pop(session_id, None)
                    self._message_cache.pop(session_id, None)
                    
                    logger.info(f"Deleted session: {session_id}")
                    return True
        
        return False
    
    def search_messages(self, session_id: str, query: str, limit: int = 10) -> List[ChatMessage]:
        """ค้นหาข้อความใน session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_messages 
                WHERE session_id = ? AND content LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, f"%{query}%", limit))
            
            rows = cursor.fetchall()
            messages = []
            
            for row in rows:
                message = ChatMessage(
                    id=row[0],
                    session_id=row[1],
                    message_type=MessageType(row[2]),
                    content=row[3],
                    timestamp=datetime.fromisoformat(row[4]),
                    metadata=json.loads(row[5]),
                    parent_message_id=row[6],
                    response_to=row[7]
                )
                messages.append(message)
            
            return messages
    
    def get_conversation_context(self, session_id: str, message_limit: int = 10) -> str:
        """ดึง context ของการสนทนา"""
        messages = self.get_messages(session_id, limit=message_limit)
        
        context = []
        for message in messages:
            role = message.message_type.value.upper()
            context.append(f"{role}: {message.content}")
        
        return "\n".join(context)
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """ลบ sessions เก่า"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get old session IDs
                cursor.execute("""
                    SELECT id FROM chat_sessions 
                    WHERE updated_at < ? AND is_active = 0
                """, (cutoff_date.isoformat(),))
                
                old_session_ids = [row[0] for row in cursor.fetchall()]
                
                if old_session_ids:
                    # Delete messages
                    placeholders = ','.join(['?' for _ in old_session_ids])
                    cursor.execute(f"DELETE FROM chat_messages WHERE session_id IN ({placeholders})", old_session_ids)
                    
                    # Delete sessions
                    cursor.execute(f"DELETE FROM chat_sessions WHERE id IN ({placeholders})", old_session_ids)
                    
                    conn.commit()
                    
                    # Remove from cache
                    for session_id in old_session_ids:
                        self._session_cache.pop(session_id, None)
                        self._message_cache.pop(session_id, None)
                    
                    logger.info(f"Cleaned up {len(old_session_ids)} old sessions")
                    return len(old_session_ids)
        
        return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติของระบบ"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total sessions
            cursor.execute("SELECT COUNT(*) FROM chat_sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Active sessions
            cursor.execute("SELECT COUNT(*) FROM chat_sessions WHERE is_active = 1")
            active_sessions = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            total_messages = cursor.fetchone()[0]
            
            # Messages by type
            cursor.execute("""
                SELECT message_type, COUNT(*) FROM chat_messages 
                GROUP BY message_type
            """)
            messages_by_type = dict(cursor.fetchall())
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM chat_sessions 
                WHERE updated_at > ?
            """, ((datetime.now() - timedelta(days=7)).isoformat(),))
            recent_sessions = cursor.fetchone()[0]
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "messages_by_type": messages_by_type,
                "recent_sessions_7d": recent_sessions,
                "cache_size": len(self._session_cache)
            }
    
    def export_session(self, session_id: str) -> Dict[str, Any]:
        """ส่งออก session เป็น JSON"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        messages = self.get_messages(session_id)
        
        return {
            "session": session.to_dict(),
            "messages": [msg.to_dict() for msg in messages],
            "exported_at": datetime.now().isoformat()
        }
    
    def import_session(self, session_data: Dict[str, Any]) -> str:
        """นำเข้า session จาก JSON"""
        session_dict = session_data["session"]
        messages_data = session_data.get("messages", [])
        
        # Create new session
        session = self.create_session(
            user_id=session_dict["user_id"],
            title=session_dict["title"],
            metadata=session_dict["metadata"]
        )
        
        # Import messages
        for msg_data in messages_data:
            self.add_message(
                session_id=session.id,
                message_type=MessageType(msg_data["message_type"]),
                content=msg_data["content"],
                metadata=msg_data["metadata"],
                parent_message_id=msg_data.get("parent_message_id"),
                response_to=msg_data.get("response_to")
            )
        
        logger.info(f"Imported session: {session.id}")
        return session.id

# Global instance
chat_memory_manager = ChatMemoryManager()
