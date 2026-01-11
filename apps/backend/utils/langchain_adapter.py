#!/usr/bin/env python3
"""
LangChain Adapter for the Unified AI Client.

This module provides a wrapper class that makes the UnifiedAIClient compatible
with the LangChain library, specifically for use with frameworks like CrewAI.
"""

from typing import Any, List, Mapping, Optional, Dict
from langchain_core.language_models.llms import LLM

from .unified_ai_client import UnifiedAIClient, get_client

class UnifiedAIClientLangChainAdapter(LLM):
    """
    A custom LangChain LLM wrapper for the UnifiedAIClient.

    This class allows any AI provider supported by the UnifiedAIClient to be
    used as a LangChain LLM, enabling integration with tools like CrewAI.
    """
    client: UnifiedAIClient
    provider: str
    model: Optional[str] = None

    def __init__(self, provider: str, model: Optional[str] = None, **kwargs):
        """
        Initializes the adapter.

        Args:
            provider (str): The name of the AI provider to use (e.g., 'ollama', 'openai').
            model (Optional[str]): The specific model name to use for this instance.
        """
        super().__init__(**kwargs)
        self.client = get_client()
        self.provider = provider
        self.model = model

    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "unified_ai_client"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Makes a call to the UnifiedAIClient.

        This method is the core of the LangChain integration. It takes a prompt,
        sends it to the configured provider via the UnifiedAIClient, and returns
        the text response.

        Args:
            prompt (str): The input prompt.
            stop (Optional[List[str]]): A list of strings to stop generation at.
                                        (Note: Not all unified client strategies may support this).
            **kwargs: Additional keyword arguments.

        Returns:
            str: The string response from the LLM.

        Raises:
            ValueError: If the API call is unsuccessful.
        """
        # This synchronous wrapper is safe to use with libraries like CrewAI,
        # which execute tools in separate threads. Calling asyncio.run() from a
        # worker thread is acceptable as it won't conflict with a main event
        # loop (e.g., from a FastAPI server).
        # WARNING: Do not call this method directly from within an existing
        # async event loop, as it will raise a RuntimeError.
        import asyncio
        return asyncio.run(self._acall(prompt, stop, **kwargs))

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Asynchronously makes a call to the UnifiedAIClient.
        """
        messages = [{"role": "user", "content": prompt}]

        # Pass the model if it's specified for this instance
        api_kwargs = {}
        if self.model:
            api_kwargs['model'] = self.model

        response = await self.client.generate_response(self.provider, messages, **api_kwargs)

        if response and response.get('success'):
            return response.get('content', '')
        else:
            error_message = response.get('error', 'Unknown error from UnifiedAIClient')
            raise ValueError(f"API call failed: {error_message}")

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"provider": self.provider, "model": self.model}
