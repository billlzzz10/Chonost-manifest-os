#!/usr/bin/env python3
"""
AI API Routes for Chonost
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.ai_router import ai_router

router = APIRouter()

class AIRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4"
    messages: List[Dict[str, str]]
    max_tokens: int = 1000
    temperature: float = 0.7

class AIResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    provider: str
    model: Optional[str] = None

@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    """Chat with AI provider"""
    try:
        result = await ai_router.route_request(request.dict())
        return AIResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_available_providers():
    """Get available AI providers"""
    providers = []
    
    if ai_router.openai_client:
        providers.append("openai")
    
    if ai_router.anthropic_client:
        providers.append("anthropic")
    
    return {"providers": providers}
