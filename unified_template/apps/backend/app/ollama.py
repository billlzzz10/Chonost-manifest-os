import json
from typing import Any, AsyncIterator, Dict

import httpx

from .settings import settings


async def stream_chat(messages: list[dict[str, Any]]) -> AsyncIterator[Dict[str, Any]]:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            url,
            json={
                "model": settings.ollama_model,
                "messages": messages,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                raw = line.strip()
                if not raw:
                    continue
                yield json.loads(raw)
