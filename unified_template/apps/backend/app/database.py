import aiosqlite
from pathlib import Path
from typing import AsyncIterator

from .settings import settings

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db() -> None:
    path = settings.sqlite_path_resolved
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(path) as db:
        await db.execute(CREATE_TABLE)
        await db.commit()


async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    conn = await aiosqlite.connect(settings.sqlite_path_resolved)
    try:
        conn.row_factory = aiosqlite.Row
        yield conn
    finally:
        await conn.close()
