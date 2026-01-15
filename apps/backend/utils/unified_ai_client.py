#!/usr/bin/env python3
"""
Unified AI Client for Multiple LLM Providers.

This module provides a single client for interacting with various Large
Language Model providers, such as OpenAI, Ollama, Anthropic, etc. It uses
a Strategy design pattern to handle the differences between provider APIs.
"""

import os
import requests
import json
import logging
import openai
import google.generativeai as genai
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ..config import settings

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Strategy Interface ---
class AIProviderStrategy(ABC):
    """
    Abstract base class for AI provider strategies.
    """
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generates a response from the AI provider.

        Args:
            messages (List[Dict[str, str]]): A list of message objects, each with 'role' and 'content'.
            **kwargs: Provider-specific arguments like model, temperature, etc.

        Returns:
            Dict[str, Any]: A dictionary containing the AI's response and other metadata.
        """
        pass

    @abstractmethod
    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates an embedding for a given text.

        Args:
            text (str): The input text to embed.
            model (Optional[str]): The specific model to use.

        Returns:
            Dict[str, Any]: A dictionary containing the embedding and other metadata.
        """
        pass

# --- Concrete Strategies ---

class OpenAIStrategy(AIProviderStrategy):
    """Strategy for interacting with OpenAI models."""
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 2000):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"OpenAIStrategy initialized for model {self.model}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generates a response using the OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', self.model),
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature)
            )
            return {
                'success': True,
                'provider': 'openai',
                'content': response.choices[0].message.content,
                'metadata': {
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'finish_reason': response.choices[0].finish_reason
                }
            }
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generates an embedding using the OpenAI API."""
        try:
            model_to_use = model or "text-embedding-3-small"
            response = self.client.embeddings.create(
                model=model_to_use,
                input=text
            )
            return {
                'success': True,
                'provider': 'openai',
                'embedding': response.data[0].embedding,
                'metadata': {
                    'model': response.model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
            }
        except Exception as e:
            logger.error(f"❌ OpenAI embedding error: {str(e)}")
            return {'success': False, 'error': str(e)}


class OllamaStrategy(AIProviderStrategy):
    """Strategy for interacting with Ollama models."""
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:6.7b-instruct", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.timeout = timeout
        logger.info(f"OllamaStrategy initialized for model {self.model} at {self.base_url}")

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generates a response from an Ollama server.
        It uses the last message as the main prompt and can handle a system prompt.
        """
        if not messages:
            return {'success': False, 'error': 'Message list cannot be empty.'}

        prompt = messages[-1]['content']
        system_prompt = next((msg['content'] for msg in messages if msg['role'] == 'system'), None)

        try:
            payload = {
                "model": kwargs.get('model', self.model),
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            if system_prompt:
                payload["system"] = system_prompt

            logger.info(f"🤖 Sending prompt to Ollama model {payload['model']}...")
            response = self.session.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes

            result = response.json()
            logger.info(f"✅ Received response from {payload['model']}.")
            return {
                'success': True,
                'provider': 'ollama',
                'content': result.get('response', ''),
                'metadata': {
                    'model': result.get('model'),
                    'total_duration': result.get('total_duration'),
                    'prompt_eval_count': result.get('prompt_eval_count'),
                    'eval_count': result.get('eval_count'),
                }
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ An error occurred while communicating with Ollama: {str(e)}")
            return {'success': False, 'error': str(e)}

    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generates an embedding using the Ollama API."""
        try:
            model_to_use = model or self.model
            logger.info(f"🤖 Generating embedding with Ollama model {model_to_use}...")
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model_to_use,
                    "prompt": text
                }
            )
            response.raise_for_status()
            result = response.json()
            return {
                'success': True,
                'provider': 'ollama',
                'embedding': result.get('embedding'),
                'metadata': {'model': model_to_use}
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ollama embedding error: {str(e)}")
            return {'success': False, 'error': str(e)}


# Placeholder for other strategies
class OpenRouterStrategy(AIProviderStrategy):
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {"provider": "openrouter", "content": "Not implemented yet"}
    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        return {'success': False, 'error': 'Not implemented'}


class GoogleStrategy(AIProviderStrategy):
    """Strategy for interacting with Google's Generative AI models."""
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
            self.model_name = model
            logger.info(f"GoogleStrategy initialized for model {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GoogleStrategy: {str(e)}")
            raise

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generates a response using the Google Generative AI API."""
        try:
            model_name = kwargs.get('model', self.model_name)
            model = genai.GenerativeModel(model_name) if model_name != self.model_name else self.model

            # Convert messages to the format expected by the Google API
            # The role for the model's response should be 'model'.
            formatted_messages = [
                {
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [{"text": msg["content"]}]
                } for msg in messages
            ]

            response = model.generate_content(
                formatted_messages,
                generation_config=genai.types.GenerationConfig(
                    # Only one candidate is needed
                    candidate_count=1,
                    temperature=kwargs.get('temperature', 0.7)
                )
            )

            return {
                'success': True,
                'provider': 'google',
                'content': response.text,
                'metadata': {
                    'model': model_name,
                    'prompt_feedback': str(response.prompt_feedback) if hasattr(response, 'prompt_feedback') else 'N/A'
                }
            }
        except Exception as e:
            logger.error(f"❌ Google AI API error: {str(e)}")
            return {'success': False, 'error': str(e)}


    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generates an embedding using the Google Generative AI API."""
        try:
            model_to_use = model or "models/embedding-001"
            result = genai.embed_content(
                model=model_to_use,
                content=text,
                task_type="retrieval_document"
            )
            return {
                'success': True,
                'provider': 'google',
                'embedding': result['embedding'],
                'metadata': {'model': model_to_use}
            }
        except Exception as e:
            logger.error(f"❌ Google embedding error: {str(e)}")
            return {'success': False, 'error': str(e)}


class AnthropicStrategy(AIProviderStrategy):
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {"provider": "anthropic", "content": "Not implemented yet"}
    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        return {'success': False, 'error': 'Not implemented'}

class DeepSeekStrategy(AIProviderStrategy):
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {"provider": "deepseek", "content": "Not implemented yet"}
    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        return {'success': False, 'error': 'Not implemented'}

class MistralStrategy(AIProviderStrategy):
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {"provider": "mistral", "content": "Not implemented yet"}
    def embed(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        return {'success': False, 'error': 'Not implemented'}


class UnifiedAIClient:
    """
    A unified client for interacting with multiple AI providers.
    It uses lazy initialization for its provider strategies.
    """
    def __init__(self, settings_override: Optional[Any] = None):
        """
        Initializes the client with a cache for provider strategies.
        An optional settings object can be injected for testing purposes.
        """
        self._strategies: Dict[str, AIProviderStrategy] = {}
        self.settings = settings_override or settings

    def get_provider(self, provider_name: str) -> Optional[AIProviderStrategy]:
        """
        Gets the strategy for a given provider, initializing it on first use.

        Args:
            provider_name (str): The name of the provider.

        Returns:
            Optional[AIProviderStrategy]: The provider strategy, or None if not configured.
        """
        provider_name = provider_name.lower()
        if provider_name in self._strategies:
            return self._strategies[provider_name]

        strategy: Optional[AIProviderStrategy] = None
        # 🛡️ Guardian: Lazily initialize strategies to improve startup time and resilience.
        if provider_name == 'openai':
            if self.settings.openai_api_key:
                strategy = OpenAIStrategy(
                    api_key=self.settings.openai_api_key,
                    base_url=getattr(self.settings, 'openai_base_url', None)
                )
        elif provider_name == 'ollama':
            # Ollama doesn't require an API key, so it's always available.
            strategy = OllamaStrategy(base_url=getattr(self.settings, 'ollama_base_url', 'http://localhost:11434'))
        elif provider_name == 'google':
            if self.settings.google_api_key:
                strategy = GoogleStrategy(api_key=self.settings.google_api_key)
        # --- Restore all providers with lazy initialization ---
        elif provider_name == 'openrouter':
            if getattr(self.settings, 'openrouter_api_key', None):
                strategy = OpenRouterStrategy()
        elif provider_name == 'anthropic':
            if getattr(self.settings, 'anthropic_api_key', None):
                strategy = AnthropicStrategy()
        elif provider_name == 'deepseek':
            if getattr(self.settings, 'deepseek_api_key', None):
                strategy = DeepSeekStrategy()
        elif provider_name == 'mistral':
            if getattr(self.settings, 'mistral_api_key', None):
                strategy = MistralStrategy()

        if strategy:
            self._strategies[provider_name] = strategy

        return strategy

    def generate_response(self, provider: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Generates a response using a specified provider.

        Args:
            provider (str): The name of the provider to use (e.g., 'openai', 'ollama').
            messages (List[Dict[str, str]]): The list of messages for the conversation.
            **kwargs: Additional provider-specific arguments.

        Returns:
            Dict[str, Any]: The response from the provider.

        Raises:
            ValueError: If the specified provider is not supported or configured.
        """
        strategy = self.get_provider(provider)
        if not strategy:
            raise ValueError(f"Provider '{provider}' is not supported or configured.")

        return strategy.generate_response(messages, **kwargs)

    def embed(self, provider: str, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates an embedding using a specified provider.

        Args:
            provider (str): The name of the provider to use.
            text (str): The text to embed.
            model (Optional[str]): The specific model to use.

        Returns:
            Dict[str, Any]: The embedding response from the provider.

        Raises:
            ValueError: If the specified provider is not supported or configured.
        """
        strategy = self.get_provider(provider)
        if not strategy:
            raise ValueError(f"Provider '{provider}' is not supported or configured.")

        return strategy.embed(text, model)

# --- Singleton Client Instance ---
_client_instance = None

def get_client() -> UnifiedAIClient:
    """
    Returns a singleton instance of the UnifiedAIClient.
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = UnifiedAIClient()
    return _client_instance
