#!/usr/bin/env python3
"""
Notion AI Client - AI Client for Notion MCP Server
ไคลเอนต์ AI สำหรับเรียกใช้งาน Notion MCP Server
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import aiohttp
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotionAIClient:
    """
    AI Client for Notion MCP Server
    ไคลเอนต์ AI สำหรับเรียกใช้งาน Notion MCP Server
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initialize Notion AI Client
        
        Args:
            server_url: URL ของ Notion MCP Server
        """
        self.server_url = server_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Notion MCP Server
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")
        
        url = f"{self.server_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"HTTP {response.status}: {response_data}")
                    raise Exception(f"HTTP {response.status}: {response_data.get('message', 'Unknown error')}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check server health
        
        Returns:
            Server health status
        """
        return await self._make_request("GET", "/health")
    
    async def initialize_notion(self, token: str) -> Dict[str, Any]:
        """
        Initialize Notion MCP Integration
        
        Args:
            token: Notion Integration Token
            
        Returns:
            Initialization result
        """
        self.token = token
        return await self._make_request(
            "POST", 
            "/api/v1/notion/init",
            data={"token": token}
        )
    
    async def create_page(
        self, 
        parent_id: str, 
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Notion page
        
        Args:
            parent_id: Parent page ID
            properties: Page properties
            children: Page children blocks
            
        Returns:
            Created page data
        """
        data = {
            "parent_id": parent_id,
            "properties": properties
        }
        if children:
            data["children"] = children
            
        return await self._make_request(
            "POST",
            "/api/v1/notion/pages",
            data=data
        )
    
    async def create_database(
        self,
        parent_id: str,
        title: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new Notion database
        
        Args:
            parent_id: Parent page ID
            title: Database title
            properties: Database properties
            
        Returns:
            Created database data
        """
        return await self._make_request(
            "POST",
            "/api/v1/notion/databases",
            data={
                "parent_id": parent_id,
                "title": title,
                "properties": properties
            }
        )
    
    async def query_database(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Query a Notion database
        
        Args:
            database_id: Database ID
            filter: Query filter
            sorts: Sort options
            
        Returns:
            Query results
        """
        data = {"database_id": database_id}
        if filter:
            data["filter"] = filter
        if sorts:
            data["sorts"] = sorts
            
        return await self._make_request(
            "POST",
            f"/api/v1/notion/databases/{database_id}/query",
            data=data
        )
    
    async def search_pages(
        self,
        query: str,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search Notion pages
        
        Args:
            query: Search query
            filter: Search filter
            
        Returns:
            Search results
        """
        data = {"query": query}
        if filter:
            data["filter"] = filter
            
        return await self._make_request(
            "POST",
            "/api/v1/notion/search",
            data=data
        )
    
    async def export_file_structure(
        self,
        file_structure: Dict[str, Any],
        parent_page_id: str
    ) -> Dict[str, Any]:
        """
        Export file structure to Notion
        
        Args:
            file_structure: File structure data
            parent_page_id: Parent page ID for export
            
        Returns:
            Export result
        """
        return await self._make_request(
            "POST",
            "/api/v1/notion/export/file-structure",
            data={
                "file_structure": file_structure,
                "parent_page_id": parent_page_id
            }
        )
    
    async def create_file_analysis_database(
        self,
        parent_page_id: str
    ) -> Dict[str, Any]:
        """
        Create file analysis database
        
        Args:
            parent_page_id: Parent page ID
            
        Returns:
            Created database data
        """
        return await self._make_request(
            "POST",
            f"/api/v1/notion/databases/file-analysis?parent_page_id={parent_page_id}"
        )
    
    async def add_file_to_database(
        self,
        database_id: str,
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add file information to database
        
        Args:
            database_id: Database ID
            file_info: File information
            
        Returns:
            Added file data
        """
        return await self._make_request(
            "POST",
            f"/api/v1/notion/databases/{database_id}/files",
            data={
                "database_id": database_id,
                "file_info": file_info
            }
        )
    
    async def get_config(self) -> Dict[str, Any]:
        """
        Get server configuration
        
        Returns:
            Server configuration
        """
        return await self._make_request("GET", "/api/v1/config")
    
    async def update_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update server configuration
        
        Args:
            config: New configuration
            
        Returns:
            Update result
        """
        return await self._make_request("PUT", "/api/v1/config", data=config)
    
    async def stop_notion_server(self) -> Dict[str, Any]:
        """
        Stop Notion MCP server
        
        Returns:
            Stop result
        """
        return await self._make_request("POST", "/api/v1/notion/stop")
    
    async def batch_export_files(
        self,
        files: List[Dict[str, Any]],
        parent_page_id: str
    ) -> Dict[str, Any]:
        """
        Batch export multiple files to Notion
        
        Args:
            files: List of file information
            parent_page_id: Parent page ID
            
        Returns:
            Batch export result
        """
        return await self._make_request(
            "POST",
            f"/api/v1/notion/batch/export?parent_page_id={parent_page_id}",
            data=files
        )

# Convenience functions for AI usage
class NotionAIHelper:
    """
    Helper class for AI to easily use Notion MCP Server
    คลาสช่วยเหลือสำหรับ AI ในการใช้งาน Notion MCP Server อย่างง่าย
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.client: Optional[NotionAIClient] = None
    
    async def setup(self, token: str) -> bool:
        """
        Setup Notion AI Client
        
        Args:
            token: Notion Integration Token
            
        Returns:
            Setup success status
        """
        try:
            self.client = NotionAIClient(self.server_url)
            await self.client.__aenter__()
            
            # Check server health
            health = await self.client.health_check()
            logger.info(f"Server health: {health}")
            
            # Initialize Notion
            result = await self.client.initialize_notion(token)
            if result.get("success"):
                logger.info("✅ Notion AI Client setup successful")
                return True
            else:
                logger.error(f"❌ Notion initialization failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.__aexit__(None, None, None)
    
    async def export_file_analysis(
        self,
        file_path: str,
        parent_page_id: str,
        database_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export file analysis to Notion
        
        Args:
            file_path: Path to file
            parent_page_id: Parent page ID
            database_id: Database ID (optional)
            
        Returns:
            Export result
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call setup() first.")
        
        try:
            # Get file info
            file_path_obj = Path(file_path)
            file_info = {
                "file_name": file_path_obj.name,
                "file_path": str(file_path_obj.absolute()),
                "file_type": file_path_obj.suffix,
                "size": file_path_obj.stat().st_size if file_path_obj.exists() else 0,
                "last_modified": file_path_obj.stat().st_mtime if file_path_obj.exists() else 0,
                "analysis_status": "pending",
                "tags": []
            }
            
            # Create file structure
            file_structure = {
                "name": file_path_obj.name,
                "type": "file",
                "path": str(file_path_obj.absolute()),
                "size": file_info["size"],
                "modified": file_info["last_modified"],
                "children": []
            }
            
            # Export to Notion
            if database_id:
                # Add to existing database
                result = await self.client.add_file_to_database(database_id, file_info)
            else:
                # Export as file structure
                result = await self.client.export_file_structure(file_structure, parent_page_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {
                "success": False,
                "message": f"Export failed: {e}",
                "error": str(e)
            }
    
    async def create_project_documentation(
        self,
        project_path: str,
        parent_page_id: str
    ) -> Dict[str, Any]:
        """
        Create project documentation in Notion
        
        Args:
            project_path: Project directory path
            parent_page_id: Parent page ID
            
        Returns:
            Documentation creation result
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call setup() first.")
        
        try:
            project_path_obj = Path(project_path)
            
            # Create project page
            project_page = await self.client.create_page(
                parent_id=parent_page_id,
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": project_path_obj.name
                                }
                            }
                        ]
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "heading_1",
                        "heading_1": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Project: {project_path_obj.name}"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"Project path: {project_path_obj.absolute()}"
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            
            if project_page.get("success"):
                # Create file analysis database
                database_result = await self.client.create_file_analysis_database(
                    parent_page_id=project_page["data"]["id"]
                )
                
                return {
                    "success": True,
                    "project_page": project_page["data"],
                    "database": database_result.get("data") if database_result.get("success") else None
                }
            else:
                return project_page
                
        except Exception as e:
            logger.error(f"Documentation creation failed: {e}")
            return {
                "success": False,
                "message": f"Documentation creation failed: {e}",
                "error": str(e)
            }

# Example usage for AI
async def example_ai_usage():
    """
    Example of how AI can use the Notion MCP Server
    ตัวอย่างการใช้งาน Notion MCP Server โดย AI
    """
    # Initialize helper
    helper = NotionAIHelper()
    
    try:
        # Setup with token
        token = os.getenv("NOTION_INTEGRATION_TOKEN")
        if not token:
            logger.error("❌ NOTION_INTEGRATION_TOKEN not found")
            return
        
        success = await helper.setup(token)
        if not success:
            logger.error("❌ Setup failed")
            return
        
        # Example: Export file analysis
        result = await helper.export_file_analysis(
            file_path="src/server/notion_mcp_integration.py",
            parent_page_id="your_parent_page_id"
        )
        logger.info(f"Export result: {result}")
        
        # Example: Create project documentation
        doc_result = await helper.create_project_documentation(
            project_path=".",
            parent_page_id="your_parent_page_id"
        )
        logger.info(f"Documentation result: {doc_result}")
        
    finally:
        await helper.cleanup()

if __name__ == "__main__":
    # Run example
    asyncio.run(example_ai_usage())
