#!/usr/bin/env python3
"""
Chat Memory Client
HTTP client สำหรับ Chat Memory API

This module provides an HTTP client for interacting with the Chat Memory API
โมดูลนี้ให้ HTTP client สำหรับโต้ตอบกับ Chat Memory API
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class ChatMemoryClient:
    """HTTP client สำหรับ Chat Memory API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """เริ่มต้น Chat Memory Client"""
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          params: Optional[Dict] = None) -> Dict[str, Any]:
        """ทำ HTTP request"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # Session Management
    
    async def create_session(self, user_id: str, title: str = "New Chat", 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """สร้าง session ใหม่"""
        data = {
            "user_id": user_id,
            "title": title,
            "metadata": metadata or {}
        }
        return await self._make_request("POST", "/api/v1/chat/sessions", data=data)
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """ดึงข้อมูล session"""
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}")
    
    async def get_user_sessions(self, user_id: str, limit: Optional[int] = None, 
                              offset: int = 0) -> List[Dict[str, Any]]:
        """ดึง sessions ของ user"""
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        
        return await self._make_request("GET", f"/api/v1/chat/users/{user_id}/sessions", params=params)
    
    async def update_session_title(self, session_id: str, title: str) -> Dict[str, Any]:
        """อัปเดตชื่อ session"""
        data = {"title": title}
        return await self._make_request("PUT", f"/api/v1/chat/sessions/{session_id}/title", data=data)
    
    async def deactivate_session(self, session_id: str) -> Dict[str, Any]:
        """ปิดใช้งาน session"""
        return await self._make_request("POST", f"/api/v1/chat/sessions/{session_id}/deactivate")
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """ลบ session"""
        return await self._make_request("DELETE", f"/api/v1/chat/sessions/{session_id}")
    
    # Message Management
    
    async def add_message(self, session_id: str, message_type: str, content: str,
                         metadata: Optional[Dict[str, Any]] = None, 
                         parent_message_id: Optional[str] = None,
                         response_to: Optional[str] = None) -> Dict[str, Any]:
        """เพิ่มข้อความใหม่"""
        data = {
            "message_type": message_type,
            "content": content,
            "metadata": metadata or {},
            "parent_message_id": parent_message_id,
            "response_to": response_to
        }
        return await self._make_request("POST", f"/api/v1/chat/sessions/{session_id}/messages", data=data)
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None, 
                          offset: int = 0) -> List[Dict[str, Any]]:
        """ดึงข้อความจาก session"""
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}/messages", params=params)
    
    async def search_messages(self, session_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """ค้นหาข้อความใน session"""
        data = {"query": query, "limit": limit}
        return await self._make_request("POST", f"/api/v1/chat/sessions/{session_id}/search", data=data)
    
    async def get_conversation_context(self, session_id: str, message_limit: int = 10) -> Dict[str, Any]:
        """ดึง context ของการสนทนา"""
        params = {"message_limit": message_limit}
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}/context", params=params)
    
    # System Management
    
    async def cleanup_old_sessions(self, days: int = 30) -> Dict[str, Any]:
        """ลบ sessions เก่า"""
        params = {"days": days}
        return await self._make_request("POST", "/api/v1/chat/cleanup", params=params)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติของระบบ"""
        return await self._make_request("GET", "/api/v1/chat/statistics")
    
    async def health_check(self) -> Dict[str, Any]:
        """ตรวจสอบสถานะของ API"""
        return await self._make_request("GET", "/api/v1/chat/health")
    
    # Import/Export
    
    async def export_session(self, session_id: str) -> Dict[str, Any]:
        """ส่งออก session เป็น JSON"""
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}/export")
    
    async def import_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """นำเข้า session จาก JSON"""
        return await self._make_request("POST", "/api/v1/chat/sessions/import", data=session_data)

class ChatMemoryHelper:
    """Helper class สำหรับการใช้งาน Chat Memory ที่ง่ายขึ้น"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """เริ่มต้น Chat Memory Helper"""
        self.base_url = base_url
        self.client: Optional[ChatMemoryClient] = None
    
    async def setup(self):
        """เริ่มต้น client"""
        self.client = ChatMemoryClient(self.base_url)
        await self.client.__aenter__()
    
    async def cleanup(self):
        """ทำความสะอาด"""
        if self.client:
            await self.client.__aexit__(None, None, None)
    
    async def start_conversation(self, user_id: str, title: str = "New Chat") -> str:
        """เริ่มต้นการสนทนาใหม่"""
        if not self.client:
            await self.setup()
        
        session = await self.client.create_session(user_id, title)
        return session["id"]
    
    async def send_message(self, session_id: str, content: str, message_type: str = "user") -> Dict[str, Any]:
        """ส่งข้อความ"""
        if not self.client:
            await self.setup()
        
        return await self.client.add_message(session_id, message_type, content)
    
    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """ดึงข้อความล่าสุด"""
        if not self.client:
            await self.setup()
        
        return await self.client.get_messages(session_id, limit=limit)
    
    async def get_conversation_history(self, session_id: str) -> str:
        """ดึงประวัติการสนทนา"""
        if not self.client:
            await self.setup()
        
        context = await self.client.get_conversation_context(session_id)
        return context["context"]
    
    async def search_conversation(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        """ค้นหาในบทสนทนา"""
        if not self.client:
            await self.setup()
        
        return await self.client.search_messages(session_id, query)
    
    async def end_conversation(self, session_id: str):
        """จบการสนทนา"""
        if not self.client:
            await self.setup()
        
        await self.client.deactivate_session(session_id)
    
    async def save_conversation(self, session_id: str, file_path: str):
        """บันทึกการสนทนาเป็นไฟล์"""
        if not self.client:
            await self.setup()
        
        export_data = await self.client.export_session(session_id)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Conversation saved to: {file_path}")

# Example usage
async def example_usage():
    """ตัวอย่างการใช้งาน"""
    async with ChatMemoryClient() as client:
        # สร้าง session ใหม่
        session = await client.create_session("user123", "Test Conversation")
        session_id = session["id"]
        
        # ส่งข้อความ
        await client.add_message(session_id, "user", "สวัสดีครับ")
        await client.add_message(session_id, "ai", "สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?")
        
        # ดึงข้อความล่าสุด
        messages = await client.get_messages(session_id, limit=5)
        print(f"Recent messages: {len(messages)}")
        
        # ดึง context
        context = await client.get_conversation_context(session_id)
        print(f"Context: {context['context']}")

if __name__ == "__main__":
    asyncio.run(example_usage())
