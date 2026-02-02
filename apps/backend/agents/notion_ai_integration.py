#!/usr/bin/env python3
"""
Notion AI Integration for Desktop Commander.
This module provides AI integration with Notion for the Desktop Commander.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.llm.notion_ai_client import NotionAIHelper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/notion_ai_integration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NotionAIIntegration:
    """
    AI Integration for Notion MCP Server.

    Attributes:
        server_url (str): The URL of the Notion MCP Server.
        helper (Optional[NotionAIHelper]): The Notion AI helper client.
        is_initialized (bool): A flag indicating if the integration is initialized.
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initializes the Notion AI Integration.
        
        Args:
            server_url (str): The URL of the Notion MCP Server.
        """
        self.server_url = server_url
        self.helper: Optional[NotionAIHelper] = None
        self.is_initialized = False
        
    async def initialize(self, token: str) -> bool:
        """
        Initializes the AI integration.
        
        Args:
            token (str): The Notion Integration Token.
            
        Returns:
            bool: The initialization success status.
        """
        try:
            self.helper = NotionAIHelper(self.server_url)
            success = await self.helper.setup(token)
            
            if success:
                self.is_initialized = True
                logger.info("✅ Notion AI Integration initialized successfully")
                return True
            else:
                logger.error("❌ Failed to initialize Notion AI Integration")
                return False
                
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            return False
    
    async def cleanup(self):
        """Cleans up resources."""
        if self.helper:
            await self.helper.cleanup()
            self.is_initialized = False
            logger.info("🧹 Notion AI Integration cleaned up")
    
    def _check_initialized(self):
        """Checks if the integration is initialized."""
        if not self.is_initialized or not self.helper:
            raise RuntimeError("Notion AI Integration not initialized. Call initialize() first.")
    
    async def analyze_and_export_file(
        self,
        file_path: str,
        parent_page_id: str,
        database_id: Optional[str] = None,
        analysis_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Analyzes a file and exports it to Notion.
        
        Args:
            file_path (str): The path to the file.
            parent_page_id (str): The ID of the parent page.
            database_id (Optional[str]): The ID of the database (optional).
            analysis_type (str): The type of analysis (basic, detailed, code).
            
        Returns:
            Dict[str, Any]: The analysis and export result.
        """
        self._check_initialized()
        
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return {
                    "success": False,
                    "message": f"File not found: {file_path}",
                    "error": "File does not exist"
                }
            
            # Basic file analysis
            file_info = {
                "file_name": file_path_obj.name,
                "file_path": str(file_path_obj.absolute()),
                "file_type": file_path_obj.suffix,
                "size": file_path_obj.stat().st_size,
                "last_modified": file_path_obj.stat().st_mtime,
                "analysis_status": "completed",
                "analysis_type": analysis_type,
                "analysis_date": datetime.now().isoformat(),
                "tags": []
            }
            
            # Enhanced analysis based on file type
            if analysis_type == "detailed":
                file_info.update(await self._detailed_file_analysis(file_path_obj))
            elif analysis_type == "code" and file_path_obj.suffix in [".py", ".js", ".ts", ".java", ".cpp", ".c"]:
                file_info.update(await self._code_analysis(file_path_obj))
            
            # Export to Notion
            if database_id:
                result = await self.helper.add_file_to_database(database_id, file_info)
            else:
                # Create file structure for export
                file_structure = {
                    "name": file_path_obj.name,
                    "type": "file",
                    "path": str(file_path_obj.absolute()),
                    "size": file_info["size"],
                    "modified": file_info["last_modified"],
                    "analysis": file_info,
                    "children": []
                }
                result = await self.helper.export_file_structure(file_structure, parent_page_id)
            
            return result
            
        except Exception as e:
            logger.error(f"File analysis failed: {e}")
            return {
                "success": False,
                "message": f"File analysis failed: {e}",
                "error": str(e)
            }
    
    async def _detailed_file_analysis(self, file_path: Path) -> Dict[str, Any]:
        """
        Performs detailed file analysis.
        
        Args:
            file_path (Path): The path to the file.
            
        Returns:
            Dict[str, Any]: Detailed analysis data.
        """
        analysis = {}
        
        try:
            # Read file content for analysis
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Basic statistics
            analysis["line_count"] = len(content.splitlines())
            analysis["word_count"] = len(content.split())
            analysis["character_count"] = len(content)
            
            # File type specific analysis
            if file_path.suffix == ".py":
                analysis.update(await self._python_analysis(content))
            elif file_path.suffix in [".js", ".ts"]:
                analysis.update(await self._javascript_analysis(content))
            elif file_path.suffix == ".md":
                analysis.update(await self._markdown_analysis(content))
            elif file_path.suffix == ".json":
                analysis.update(await self._json_analysis(content))
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Detailed analysis failed for {file_path}: {e}")
            return {"analysis_error": str(e)}
    
    async def _python_analysis(self, content: str) -> Dict[str, Any]:
        """
        Analyzes Python code.

        Args:
            content (str): The content of the Python code.

        Returns:
            Dict[str, Any]: The analysis result.
        """
        analysis = {"language": "Python"}
        
        try:
            lines = content.splitlines()
            
            # Count imports, functions, classes
            imports = [line for line in lines if line.strip().startswith(('import ', 'from '))]
            functions = [line for line in lines if line.strip().startswith('def ')]
            classes = [line for line in lines if line.strip().startswith('class ')]
            
            analysis.update({
                "import_count": len(imports),
                "function_count": len(functions),
                "class_count": len(classes),
                "imports": imports[:10],  # First 10 imports
                "functions": [f.strip() for f in functions[:10]],  # First 10 functions
                "classes": [c.strip() for c in classes[:10]]  # First 10 classes
            })
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    async def _javascript_analysis(self, content: str) -> Dict[str, Any]:
        """
        Analyzes JavaScript/TypeScript code.

        Args:
            content (str): The content of the JavaScript/TypeScript code.

        Returns:
            Dict[str, Any]: The analysis result.
        """
        analysis = {"language": "JavaScript/TypeScript"}
        
        try:
            lines = content.splitlines()
            
            # Count imports, functions, classes
            imports = [line for line in lines if line.strip().startswith(('import ', 'const ', 'let ', 'var '))]
            functions = [line for line in lines if 'function ' in line or '=>' in line]
            classes = [line for line in lines if line.strip().startswith('class ')]
            
            analysis.update({
                "import_count": len(imports),
                "function_count": len(functions),
                "class_count": len(classes)
            })
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    async def _markdown_analysis(self, content: str) -> Dict[str, Any]:
        """
        Analyzes Markdown content.

        Args:
            content (str): The content of the Markdown file.

        Returns:
            Dict[str, Any]: The analysis result.
        """
        analysis = {"language": "Markdown"}
        
        try:
            lines = content.splitlines()
            
            # Count headers, links, images
            headers = [line for line in lines if line.strip().startswith('#')]
            links = [line for line in lines if '[' in line and '](' in line]
            images = [line for line in lines if '![' in line and '](' in line]
            
            analysis.update({
                "header_count": len(headers),
                "link_count": len(links),
                "image_count": len(images)
            })
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    async def _json_analysis(self, content: str) -> Dict[str, Any]:
        """
        Analyzes JSON content.

        Args:
            content (str): The content of the JSON file.

        Returns:
            Dict[str, Any]: The analysis result.
        """
        analysis = {"language": "JSON"}
        
        try:
            data = json.loads(content)
            
            if isinstance(data, dict):
                analysis["structure"] = "object"
                analysis["key_count"] = len(data.keys())
                analysis["top_level_keys"] = list(data.keys())[:10]
            elif isinstance(data, list):
                analysis["structure"] = "array"
                analysis["item_count"] = len(data)
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    async def _code_analysis(self, file_path: Path) -> Dict[str, Any]:
        """
        Performs code-specific analysis.
        
        Args:
            file_path (Path): The path to the code file.
            
        Returns:
            Dict[str, Any]: The code analysis data.
        """
        return await self._detailed_file_analysis(file_path)
    
    async def batch_analyze_directory(
        self,
        directory_path: str,
        parent_page_id: str,
        database_id: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        analysis_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Batch analyzes a directory and exports it to Notion.
        
        Args:
            directory_path (str): The path to the directory.
            parent_page_id (str): The ID of the parent page.
            database_id (Optional[str]): The ID of the database (optional).
            file_patterns (Optional[List[str]]): File patterns to include (e.g., ["*.py", "*.js"]).
            analysis_type (str): The type of analysis.
            
        Returns:
            Dict[str, Any]: The batch analysis result.
        """
        self._check_initialized()
        
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                return {
                    "success": False,
                    "message": f"Directory not found: {directory_path}",
                    "error": "Directory does not exist"
                }
            
            # Find files to analyze
            files_to_analyze = []
            
            if file_patterns:
                for pattern in file_patterns:
                    files_to_analyze.extend(directory.rglob(pattern))
            else:
                # Default patterns
                default_patterns = ["*.py", "*.js", "*.ts", "*.md", "*.json", "*.txt"]
                for pattern in default_patterns:
                    files_to_analyze.extend(directory.rglob(pattern))
            
            # Remove duplicates
            files_to_analyze = list(set(files_to_analyze))
            
            logger.info(f"Found {len(files_to_analyze)} files to analyze")
            
            # Analyze each file
            results = []
            for file_path in files_to_analyze:
                try:
                    result = await self.analyze_and_export_file(
                        str(file_path),
                        parent_page_id,
                        database_id,
                        analysis_type
                    )
                    results.append({
                        "file": str(file_path),
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "file": str(file_path),
                        "result": {
                            "success": False,
                            "error": str(e)
                        }
                    })
            
            # Summary
            successful = sum(1 for r in results if r["result"].get("success", False))
            failed = len(results) - successful
            
            return {
                "success": True,
                "message": f"Batch analysis completed: {successful} successful, {failed} failed",
                "data": {
                    "total_files": len(results),
                    "successful": successful,
                    "failed": failed,
                    "results": results
                }
            }
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return {
                "success": False,
                "message": f"Batch analysis failed: {e}",
                "error": str(e)
            }
    
    async def create_project_documentation(
        self,
        project_path: str,
        parent_page_id: str,
        include_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Creates comprehensive project documentation.
        
        Args:
            project_path (str): The path to the project directory.
            parent_page_id (str): The ID of the parent page.
            include_analysis (bool): Whether to include file analysis.
            
        Returns:
            Dict[str, Any]: The documentation creation result.
        """
        self._check_initialized()
        
        try:
            # Create project documentation
            doc_result = await self.helper.create_project_documentation(
                project_path,
                parent_page_id
            )
            
            if doc_result.get("success") and include_analysis:
                # Add file analysis
                database_id = doc_result.get("database", {}).get("id")
                if database_id:
                    analysis_result = await self.batch_analyze_directory(
                        project_path,
                        parent_page_id,
                        database_id,
                        analysis_type="detailed"
                    )
                    doc_result["file_analysis"] = analysis_result
            
            return doc_result
            
        except Exception as e:
            logger.error(f"Project documentation creation failed: {e}")
            return {
                "success": False,
                "message": f"Project documentation creation failed: {e}",
                "error": str(e)
            }

# Example usage for Desktop Commander
async def example_desktop_commander_integration():
    """
    Example of how Desktop Commander can use Notion AI Integration.
    """
    # Initialize integration
    integration = NotionAIIntegration()
    
    try:
        # Get token from environment
        token = os.getenv("NOTION_INTEGRATION_TOKEN")
        if not token:
            logger.error("❌ NOTION_INTEGRATION_TOKEN not found")
            return
        
        # Initialize
        success = await integration.initialize(token)
        if not success:
            logger.error("❌ Initialization failed")
            return
        
        # Example: Analyze single file
        result = await integration.analyze_and_export_file(
            file_path="src/server/notion_mcp_integration.py",
            parent_page_id="your_parent_page_id",
            analysis_type="detailed"
        )
        logger.info(f"Single file analysis: {result}")
        
        # Example: Batch analyze directory
        batch_result = await integration.batch_analyze_directory(
            directory_path="src",
            parent_page_id="your_parent_page_id",
            file_patterns=["*.py", "*.md"],
            analysis_type="detailed"
        )
        logger.info(f"Batch analysis: {batch_result}")
        
        # Example: Create project documentation
        doc_result = await integration.create_project_documentation(
            project_path=".",
            parent_page_id="your_parent_page_id",
            include_analysis=True
        )
        logger.info(f"Project documentation: {doc_result}")
        
    finally:
        await integration.cleanup()

if __name__ == "__main__":
    # Run example
    asyncio.run(example_desktop_commander_integration())
