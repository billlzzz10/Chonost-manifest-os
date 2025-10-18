from typing import List, Dict, Any
import aiosqlite

async def append_message(db: aiosqlite.Connection, conversation_id: str, role: str, content: str) -> None:
    await db.execute(
        'INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
        (conversation_id, role, content),
    )
    await db.commit()

async def list_messages(db: aiosqlite.Connection, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    cursor = await db.execute(
        'SELECT id, conversation_id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT ?',
        (conversation_id, limit),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

