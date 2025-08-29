#!/usr/bin/env python3
"""
AI Router Service for Chonost
Routes requests to appropriate AI providers
"""

import asyncio
from typing import Dict, Any, Optional
import openai
import anthropic
from qdrant_client import QdrantClient
from core.config import settings

class AIRouter:
    """Routes AI requests to appropriate providers"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.qdrant_client = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup AI provider clients"""
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        
        if settings.QDRANT_URL:
            self.qdrant_client = QdrantClient(settings.QDRANT_URL)
    
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route AI request to appropriate provider"""
        provider = request.get("provider", "openai")
        model = request.get("model", "gpt-4")
        
        if provider == "openai" and self.openai_client:
            return await self._handle_openai_request(request)
        elif provider == "anthropic" and self.anthropic_client:
            return await self._handle_anthropic_request(request)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _handle_openai_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OpenAI request"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=request.get("model", "gpt-4"),
                messages=request.get("messages", []),
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7)
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "provider": "openai",
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }
    
    async def _handle_anthropic_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Anthropic request"""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=request.get("model", "claude-3-sonnet-20240229"),
                max_tokens=request.get("max_tokens", 1000),
                messages=request.get("messages", [])
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "provider": "anthropic",
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "anthropic"
            }

# Global AI router instance
ai_router = AIRouter()
