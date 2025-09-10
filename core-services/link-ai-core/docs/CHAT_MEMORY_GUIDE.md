# 🧠 Chat Memory System Guide

## 📋 ภาพรวม

ระบบ Chat Memory เป็นระบบจัดการ Memory สำหรับการแชตจาก UI ที่จะสร้างในอนาคต ระบบนี้ให้ความสามารถในการ:

- **จัดการ Sessions** - สร้าง, อัปเดต, ลบ sessions
- ** จัดการ Messages** - เพิ่ม, ดึง, ค้นหาข้อความ
- ** Context Management** - จัดการ context ของการสนทนา
- ** Search & Export** - ค้นหาและส่งออกข้อมูล
- ** Statistics** - สถิติการใช้งาน

## 🏗️ สถาปัตยกรรม

```
Chat Memory System
├── Memory Manager (SQLite + Cache)
├── RESTful API (FastAPI)
├── HTTP Client (aiohttp)
└── Helper Classes
```

### ไฟล์หลัก:
- ` src/memory/chat_memory_manager.py` - Core Memory Management
- ` src/server/chat_memory_api.py` - RESTful API Endpoints
- ` src/client/chat_memory_client.py` - HTTP Client
- ` test_chat_memory.py` - Test Suite

## 🚀 การใช้งาน

### 1. ** เริ่มต้นระบบ** ```python
from memory.chat_memory_manager import chat_memory_manager

# ระบบจะเริ่มต้นอัตโนมัติ
print("Chat Memory System ready!")
```

### 2. ** สร้าง Session** ```python
# สร้าง session ใหม่
session = chat_memory_manager.create_session(
    user_id="user123",
    title="My Chat Session",
    metadata={"category": "work", "priority": "high"}
)

session_id = session.id
print(f"Created session: {session_id}")
```

### 3. ** เพิ่มข้อความ** ```python
from memory.chat_memory_manager import MessageType

# เพิ่มข้อความของผู้ใช้
user_message = chat_memory_manager.add_message(
    session_id=session_id,
    message_type=MessageType.USER,
    content="สวัสดีครับ",
    metadata={"emotion": "friendly"}
)

# เพิ่มข้อความของ AI
ai_message = chat_memory_manager.add_message(
    session_id=session_id,
    message_type=MessageType.AI,
    content="สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?",
    response_to=user_message.id,
    metadata={"model": "gpt-4", "response_time": 0.5}
)
```

### 4. ** ดึงข้อมูล** ```python
# ดึง session
session = chat_memory_manager.get_session(session_id)

# ดึงข้อความ
messages = chat_memory_manager.get_messages(session_id, limit=10)

# ดึง context
context = chat_memory_manager.get_conversation_context(session_id, message_limit=5)

# ค้นหาข้อความ
search_results = chat_memory_manager.search_messages(session_id, "สวัสดี")
```

## 🌐 การใช้งานผ่าน API

### 1. ** เริ่มต้น API Server** ```python
# ใน FastAPI app
from server.chat_memory_api import router
app.include_router(router)
```

### 2. ** ใช้ HTTP Client** ```python
from client.chat_memory_client import ChatMemoryClient

async with ChatMemoryClient() as client:
    # สร้าง session
    session = await client.create_session("user123", "API Test")

    # เพิ่มข้อความ
    await client.add_message(session["id"], "user", "Hello")
    await client.add_message(session["id"], "ai", "Hi there!")

    # ดึงข้อความ
    messages = await client.get_messages(session["id"])
```

### 3. ** ใช้ Helper Class** ```python
from client.chat_memory_client import ChatMemoryHelper

helper = ChatMemoryHelper()
await helper.setup()

# เริ่มต้นการสนทนา
session_id = await helper.start_conversation("user123", "Helper Test")

# ส่งข้อความ
await helper.send_message(session_id, "Hello", "user")
await helper.send_message(session_id, "Hi!", "ai")

# ดึงประวัติ
history = await helper.get_conversation_history(session_id)

await helper.cleanup()
```

## 📊 API Endpoints

### ** Session Management** - ` POST /api/v1/chat/sessions` - สร้าง session ใหม่
- ` GET /api/v1/chat/sessions/{session_id}` - ดึงข้อมูล session
- ` GET /api/v1/chat/users/{user_id}/sessions` - ดึง sessions ของ user
- ` PUT /api/v1/chat/sessions/{session_id}/title` - อัปเดตชื่อ session
- ` POST /api/v1/chat/sessions/{session_id}/deactivate` - ปิดใช้งาน session
- ` DELETE /api/v1/chat/sessions/{session_id}` - ลบ session

### ** Message Management** - ` POST /api/v1/chat/sessions/{session_id}/messages` - เพิ่มข้อความ
- ` GET /api/v1/chat/sessions/{session_id}/messages` - ดึงข้อความ
- ` POST /api/v1/chat/sessions/{session_id}/search` - ค้นหาข้อความ
- ` GET /api/v1/chat/sessions/{session_id}/context` - ดึง context

### ** System Management** - ` GET /api/v1/chat/statistics` - สถิติระบบ
- ` POST /api/v1/chat/cleanup` - ลบ sessions เก่า
- ` GET /api/v1/chat/health` - ตรวจสอบสถานะ

### ** Import/Export** - ` GET /api/v1/chat/sessions/{session_id}/export` - ส่งออก session
- ` POST /api/v1/chat/sessions/import` - นำเข้า session

## 🔧 การตั้งค่า

### ** Database Configuration** ```python
# เปลี่ยน path ของ database
chat_memory_manager = ChatMemoryManager(db_path="custom/path/chat_memory.db")
```

### ** Cache Configuration** ```python
# ตั้งค่า cache TTL (ในวินาที)
chat_memory_manager._cache_ttl = 7200  # 2 hours
```

### ** API Configuration** ```python
# เปลี่ยน base URL ของ API
client = ChatMemoryClient(base_url="http://localhost:8080")
```

## 🧪 การทดสอบ

### ** รันการทดสอบทั้งหมด** ```bash
python test_chat_memory.py
```

### ** ทดสอบเฉพาะส่วน** ```python
# ทดสอบ Memory Manager
session_id = await test_chat_memory_manager()

# ทดสอบ API
session_id = await test_chat_memory_api()

# ทดสอบ Helper
await test_chat_memory_helper()
```

## 📈 สถิติและ Monitoring

### ** ดึงสถิติ** ```python
stats = chat_memory_manager.get_statistics()
print(f"Total sessions: {stats['total_sessions']}")
print(f"Total messages: {stats['total_messages']}")
print(f"Cache size: {stats['cache_size']}")
```

### ** Health Check** ```python
health = await client.health_check()
print(f"Status: {health['status']}")
print(f"Database: {health['database']}")
```

## 🔍 การค้นหาและ Export

### ** ค้นหาข้อความ** ```python
# ค้นหาใน session
results = chat_memory_manager.search_messages(session_id, "keyword")

# ค้นหาผ่าน API
results = await client.search_messages(session_id, "keyword")
```

### ** Export/Import** ```python
# ส่งออก session
export_data = chat_memory_manager.export_session(session_id)

# บันทึกเป็นไฟล์
with open("session_export.json", "w") as f:
    json.dump(export_data, f, indent=2)

# นำเข้า session
new_session_id = chat_memory_manager.import_session(export_data)
```

## 🛡 ️ ความปลอดภัย

### ** Data Validation** - ตรวจสอบ message type ที่ถูกต้อง
- ตรวจสอบ session ID ที่มีอยู่
- ตรวจสอบ user permissions

### ** Error Handling** ```python
try:
    session = chat_memory_manager.get_session("invalid_id")
except Exception as e:
    print(f"Error: {e}")
```

## 🔄 การบำรุงรักษา

### ** Cleanup Old Sessions** ```python
# ลบ sessions เก่ากว่า 30 วัน
deleted_count = chat_memory_manager.cleanup_old_sessions(days=30)
print(f"Deleted {deleted_count} old sessions")
```

### ** Database Maintenance** ```python
# ตรวจสอบ database integrity
import sqlite3
conn = sqlite3.connect("data/chat_memory.db")
conn.execute("PRAGMA integrity_check")
```

## 🎯 การใช้งานกับ UI

### ** ตัวอย่างการใช้งานกับ React/Vue** ```javascript
// สร้าง session
const session = await fetch('/api/v1/chat/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: 'user123',
        title: 'New Chat'
    })
}).then(r => r.json());

// ส่งข้อความ
await fetch(` /api/v1/chat/sessions/${session.id}/messages` , {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message_type: 'user',
        content: 'Hello'
    })
});
```

### ** ตัวอย่างการใช้งานกับ Python UI** ```python
import tkinter as tk
from client.chat_memory_client import ChatMemoryHelper

class ChatUI:
    def __init__(self):
        self.helper = ChatMemoryHelper()
        self.session_id = None

    async def start_chat(self):
        self.session_id = await self.helper.start_conversation("user123", "UI Chat")

    async def send_message(self, content):
        await self.helper.send_message(self.session_id, content, "user")
        # Get AI response
        ai_response = "AI response here"
        await self.helper.send_message(self.session_id, ai_response, "ai")
```

## 📚 ข้อมูลเพิ่มเติม

- ** Database Schema**: SQLite tables สำหรับ sessions และ messages
- ** Cache Strategy**: In-memory cache สำหรับ performance
- ** Thread Safety**: Thread-safe operations ด้วย locks
- ** Error Recovery**: Automatic database recovery
- ** Performance**: Optimized queries และ indexes

- --

* * หมายเหตุ**: ระบบ Chat Memory พร้อมสำหรับการใช้งานกับ UI ที่จะสร้างในอนาคต และรองรับการขยายตัวในอนาคต

