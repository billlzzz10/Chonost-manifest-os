from collections.abc import AsyncIterator
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from .database import get_db
from .memory import append_message, list_messages
from .ollama import stream_chat

router = APIRouter()


@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/memory/{conversation_id}")
async def get_memory(conversation_id: str, limit: int = 50, db=Depends(get_db)):
    messages = await list_messages(db, conversation_id, limit)
    return {"conversation_id": conversation_id, "messages": messages}


@router.post("/memory/{conversation_id}")
async def post_memory(conversation_id: str, payload: Dict[str, Any], db=Depends(get_db)):
    role = payload.get("role", "user")
    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    await append_message(db, conversation_id, role, content)
    return {"status": "stored"}


@router.post("/chat/stream")
async def chat_stream(payload: Dict[str, Any], db=Depends(get_db)):
    conversation_id = payload.get("conversation_id", "default")
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be provided")

    if messages:
        last = messages[-1]
        await append_message(
            db,
            conversation_id,
            last.get("role", "user"),
            last.get("content", ""),
        )

    async def event_source() -> AsyncIterator[bytes]:
        async for chunk in stream_chat(messages):
            delta = chunk.get("message", {}).get("content")
            if delta:
                await append_message(db, conversation_id, "assistant", delta)
                yield (delta + "\n").encode("utf-8")

    return StreamingResponse(event_source(), media_type="text/plain")
