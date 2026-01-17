from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..utils.unified_ai_client import get_client

router = APIRouter()

class ChatRequest(BaseModel):
    provider: str
    messages: List[Dict[str, str]]
    model: str = None
    temperature: float = 0.7


@router.get("/providers")
async def get_providers():
    """
    Returns a list of available AI providers.
    """
    client = get_client()
    return {"providers": client.get_available_providers()}


@router.get("/providers/{provider_name}/models")
async def get_models(provider_name: str):
    """
    Returns a list of available models for a given provider.
    """
    # In a real application, this would fetch from the provider's API
    # or a configuration file. For now, we'll use a hardcoded list.
    models = {
        "openai": ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
        "google": ["gemini-1.5-flash", "gemini-1.0-pro"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
        "ollama": ["llama3.1:8b", "deepseek-coder:6.7b-instruct"],
    }
    provider_models = models.get(provider_name.lower(), [])
    if not provider_models:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"models": provider_models}


@router.post("/chat")
async def chat_with_provider(request: ChatRequest):
    """
    Handles a chat request with a specified AI provider, including special commands.
    """
    try:
        client = get_client()
        last_message = request.messages[-1]['content'].lower() if request.messages else ""

        if last_message == "/help":
            return {
                "success": True,
                "provider": "system",
                "content": """Available commands:
- `/code <description>` - Generate code
- `/analyze <content>` - Analyze and improve content
- `/help` - Show this help message""",
            }

        if last_message.startswith("/code "):
            description = request.messages[-1]['content'][6:]
            request.messages[-1]['content'] = f"Generate a code snippet for the following description: {description}"
        elif last_message.startswith("/analyze "):
            content = request.messages[-1]['content'][9:]
            request.messages[-1]['content'] = f"Analyze and suggest improvements for the following content: {content}"

        response = client.generate_response(
            provider=request.provider,
            messages=request.messages,
            model=request.model,
            temperature=request.temperature
        )
        if not response.get('success'):
            raise HTTPException(status_code=500, detail=response.get('error', 'Unknown error'))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
