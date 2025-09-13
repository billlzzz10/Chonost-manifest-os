#!/usr/bin/env python3
"""
Chat Memory Client.
This module provides an HTTP client for interacting with the Chat Memory API.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class ChatMemoryClient:
    """
    An HTTP client for the Chat Memory API.

    Attributes:
        base_url (str): The base URL of the Chat Memory API.
        session (Optional[aiohttp.ClientSession]): The aiohttp client session.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initializes the Chat Memory Client.

        Args:
            base_url (str, optional): The base URL of the Chat Memory API. Defaults to "http://localhost:8000".
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Initializes the client session for async context management."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the client session for async context management."""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Makes an HTTP request.

        Args:
            method (str): The HTTP method.
            endpoint (str): The API endpoint.
            data (Optional[Dict], optional): The request data. Defaults to None.
            params (Optional[Dict], optional): The request parameters. Defaults to None.

        Returns:
            Dict[str, Any]: The JSON response from the API.
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # Session Management
    
    async def create_session(self, user_id: str, title: str = "New Chat", 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Creates a new session.

        Args:
            user_id (str): The ID of the user.
            title (str, optional): The title of the session. Defaults to "New Chat".
            metadata (Optional[Dict[str, Any]], optional): Metadata for the session. Defaults to None.

        Returns:
            Dict[str, Any]: The created session.
        """
        data = {
            "user_id": user_id,
            "title": title,
            "metadata": metadata or {}
        }
        return await self._make_request("POST", "/api/v1/chat/sessions", data=data)
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Gets session information.

        Args:
            session_id (str): The ID of the session.

        Returns:
            Dict[str, Any]: The session information.
        """
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}")
    
    async def get_user_sessions(self, user_id: str, limit: Optional[int] = None, 
                              offset: int = 0) -> List[Dict[str, Any]]:
        """
        Gets a user's sessions.

        Args:
            user_id (str): The ID of the user.
            limit (Optional[int], optional): The maximum number of sessions to return. Defaults to None.
            offset (int, optional): The offset for pagination. Defaults to 0.

        Returns:
            List[Dict[str, Any]]: A list of the user's sessions.
        """
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        
        return await self._make_request("GET", f"/api/v1/chat/users/{user_id}/sessions", params=params)
    
    async def update_session_title(self, session_id: str, title: str) -> Dict[str, Any]:
        """
        Updates a session's title.

        Args:
            session_id (str): The ID of the session.
            title (str): The new title.

        Returns:
            Dict[str, Any]: The updated session.
        """
        data = {"title": title}
        return await self._make_request("PUT", f"/api/v1/chat/sessions/{session_id}/title", data=data)
    
    async def deactivate_session(self, session_id: str) -> Dict[str, Any]:
        """
        Deactivates a session.

        Args:
            session_id (str): The ID of the session.

        Returns:
            Dict[str, Any]: The result of the deactivation.
        """
        return await self._make_request("POST", f"/api/v1/chat/sessions/{session_id}/deactivate")
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Deletes a session.

        Args:
            session_id (str): The ID of the session.

        Returns:
            Dict[str, Any]: The result of the deletion.
        """
        return await self._make_request("DELETE", f"/api/v1/chat/sessions/{session_id}")
    
    # Message Management
    
    async def add_message(self, session_id: str, message_type: str, content: str,
                         metadata: Optional[Dict[str, Any]] = None, 
                         parent_message_id: Optional[str] = None,
                         response_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Adds a new message.

        Args:
            session_id (str): The ID of the session.
            message_type (str): The type of the message.
            content (str): The content of the message.
            metadata (Optional[Dict[str, Any]], optional): Metadata for the message. Defaults to None.
            parent_message_id (Optional[str], optional): The ID of the parent message. Defaults to None.
            response_to (Optional[str], optional): The ID of the message being responded to. Defaults to None.

        Returns:
            Dict[str, Any]: The added message.
        """
        data = {
            "message_type": message_type,
            "content": content,
            "metadata": metadata or {},
            "parent_message_id": parent_message_id,
            "response_to": response_to
        }
        return await self._make_request("POST", f"/api/v1/chat/sessions/{session_id}/messages", data=data)
    
    async def get_messages(self, session_id: str, limit: Optional[int] = None, 
                          offset: int = 0) -> List[Dict[str, Any]]:
        """
        Gets messages from a session.

        Args:
            session_id (str): The ID of the session.
            limit (Optional[int], optional): The maximum number of messages to return. Defaults to None.
            offset (int, optional): The offset for pagination. Defaults to 0.

        Returns:
            List[Dict[str, Any]]: A list of messages.
        """
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}/messages", params=params)
    
    async def search_messages(self, session_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Searches for messages in a session.

        Args:
            session_id (str): The ID of the session.
            query (str): The search query.
            limit (int, optional): The maximum number of results to return. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: A list of search results.
        """
        data = {"query": query, "limit": limit}
        return await self._make_request("POST", f"/api/v1/chat/sessions/{session_id}/search", data=data)
    
    async def get_conversation_context(self, session_id: str, message_limit: int = 10) -> Dict[str, Any]:
        """
        Gets the conversation context.

        Args:
            session_id (str): The ID of the session.
            message_limit (int, optional): The maximum number of messages to include in the context. Defaults to 10.

        Returns:
            Dict[str, Any]: The conversation context.
        """
        params = {"message_limit": message_limit}
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}/context", params=params)
    
    # System Management
    
    async def cleanup_old_sessions(self, days: int = 30) -> Dict[str, Any]:
        """
        Deletes old sessions.

        Args:
            days (int, optional): The minimum age of sessions to delete. Defaults to 30.

        Returns:
            Dict[str, Any]: The result of the cleanup.
        """
        params = {"days": days}
        return await self._make_request("POST", "/api/v1/chat/cleanup", params=params)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Gets system statistics.

        Returns:
            Dict[str, Any]: The system statistics.
        """
        return await self._make_request("GET", "/api/v1/chat/statistics")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Checks the status of the API.

        Returns:
            Dict[str, Any]: The health check status.
        """
        return await self._make_request("GET", "/api/v1/chat/health")
    
    # Import/Export
    
    async def export_session(self, session_id: str) -> Dict[str, Any]:
        """
        Exports a session to JSON.

        Args:
            session_id (str): The ID of the session to export.

        Returns:
            Dict[str, Any]: The exported session data.
        """
        return await self._make_request("GET", f"/api/v1/chat/sessions/{session_id}/export")
    
    async def import_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imports a session from JSON.

        Args:
            session_data (Dict[str, Any]): The session data to import.

        Returns:
            Dict[str, Any]: The imported session.
        """
        return await self._make_request("POST", "/api/v1/chat/sessions/import", data=session_data)

class ChatMemoryHelper:
    """A helper class for easier use of the Chat Memory API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initializes the ChatMemoryHelper.

        Args:
            base_url (str, optional): The base URL of the Chat Memory API. Defaults to "http://localhost:8000".
        """
        self.base_url = base_url
        self.client: Optional[ChatMemoryClient] = None
    
    async def setup(self):
        """Initializes the client."""
        self.client = ChatMemoryClient(self.base_url)
        await self.client.__aenter__()
    
    async def cleanup(self):
        """Cleans up resources."""
        if self.client:
            await self.client.__aexit__(None, None, None)
    
    async def start_conversation(self, user_id: str, title: str = "New Chat") -> str:
        """
        Starts a new conversation.

        Args:
            user_id (str): The ID of the user.
            title (str, optional): The title of the conversation. Defaults to "New Chat".

        Returns:
            str: The ID of the new session.
        """
        if not self.client:
            await self.setup()
        
        session = await self.client.create_session(user_id, title)
        return session["id"]
    
    async def send_message(self, session_id: str, content: str, message_type: str = "user") -> Dict[str, Any]:
        """
        Sends a message.

        Args:
            session_id (str): The ID of the session.
            content (str): The content of the message.
            message_type (str, optional): The type of the message. Defaults to "user".

        Returns:
            Dict[str, Any]: The sent message.
        """
        if not self.client:
            await self.setup()
        
        return await self.client.add_message(session_id, message_type, content)
    
    async def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Gets recent messages.

        Args:
            session_id (str): The ID of the session.
            limit (int, optional): The maximum number of messages to return. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: A list of recent messages.
        """
        if not self.client:
            await self.setup()
        
        return await self.client.get_messages(session_id, limit=limit)
    
    async def get_conversation_history(self, session_id: str) -> str:
        """
        Gets the conversation history.

        Args:
            session_id (str): The ID of the session.

        Returns:
            str: The conversation history.
        """
        if not self.client:
            await self.setup()
        
        context = await self.client.get_conversation_context(session_id)
        return context["context"]
    
    async def search_conversation(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Searches within a conversation.

        Args:
            session_id (str): The ID of the session.
            query (str): The search query.

        Returns:
            List[Dict[str, Any]]: A list of search results.
        """
        if not self.client:
            await self.setup()
        
        return await self.client.search_messages(session_id, query)
    
    async def end_conversation(self, session_id: str):
        """
        Ends a conversation.

        Args:
            session_id (str): The ID of the session.
        """
        if not self.client:
            await self.setup()
        
        await self.client.deactivate_session(session_id)
    
    async def save_conversation(self, session_id: str, file_path: str):
        """
        Saves a conversation to a file.

        Args:
            session_id (str): The ID of the session.
            file_path (str): The path to the file to save the conversation to.
        """
        if not self.client:
            await self.setup()
        
        export_data = await self.client.export_session(session_id)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Conversation saved to: {file_path}")

# Example usage
async def example_usage():
    """Example usage of the ChatMemoryClient."""
    async with ChatMemoryClient() as client:
        # Create a new session
        session = await client.create_session("user123", "Test Conversation")
        session_id = session["id"]
        
        # Send messages
        await client.add_message(session_id, "user", "Hello")
        await client.add_message(session_id, "ai", "Hi! How can I help you?")
        
        # Get recent messages
        messages = await client.get_messages(session_id, limit=5)
        print(f"Recent messages: {len(messages)}")
        
        # Get context
        context = await client.get_conversation_context(session_id)
        print(f"Context: {context['context']}")

if __name__ == "__main__":
    asyncio.run(example_usage())
