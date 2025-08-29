"""
Context Manager for Chonost

This module provides context management for prompt injection including:
- Story context loading and management
- Project status tracking
- User preferences management
- Tool availability tracking
"""

import json
import logging
import sqlite3
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextManager:
    """Manager for context data injection into prompts"""
    
    def __init__(self, db_path: str = "chonost_context.db"):
        self.db_path = db_path
        self._init_database()
        self.story_context = self._load_story_context()
        self.project_status = self._load_project_status()
        self.user_preferences = self._load_user_preferences()
        self.available_tools = self._load_available_tools()
    
    def _init_database(self):
        """Initialize context database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create story context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                context_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Create project status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                last_updated TEXT NOT NULL
            )
        """)
        
        # Create user preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        """)
        
        # Create available tools table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS available_tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                tool_schema TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                last_updated TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_story_context(self) -> Dict[str, Any]:
        """Load story context from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT context_type, context_data FROM story_context ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            context = {}
            for row in rows:
                context_type, context_data = row
                context[context_type] = json.loads(context_data)
            
            # Default story context for "Bound Fate"
            if not context:
                context = {
                    "main_story": {
                        "title": "Bound Fate: The Arcana Burden",
                        "protagonist": "Ignis",
                        "setting": "Central Temple",
                        "themes": ["Forgotten History", "The Burden of Knowledge", "The Morality of Truth"],
                        "current_plot_point": "Ignis has discovered the truth about the Fourth Moon"
                    },
                    "characters": {
                        "Ignis": {
                            "role": "Blacksmith",
                            "personality": "Defensive, protective, hesitant",
                            "fighting_style": "Uses brute strength and surroundings",
                            "motivation": "Protect Liosandra"
                        },
                        "Mia": {
                            "role": "Lunar Sentinel",
                            "personality": "Disciplined, cold, duty-bound",
                            "fighting_style": "Precise, efficient, trained",
                            "motivation": "Twisted sense of duty"
                        },
                        "Liosandra": {
                            "role": "Disgraced Historian",
                            "personality": "Obsessive, determined",
                            "motivation": "Find the World Tree"
                        }
                    },
                    "world_lore": {
                        "status_system": "A burden, not a game, gives cryptic quests",
                        "fourth_moon": "Suppressed history by Tri-Moon Cult",
                        "world_tree": "Ancient artifact of power"
                    }
                }
            
            return context
            
        except Exception as e:
            logger.error(f"Error loading story context: {e}")
            return {}
    
    def _load_project_status(self) -> Dict[str, Any]:
        """Load project status from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT component, status, details FROM project_status ORDER BY last_updated DESC")
            rows = cursor.fetchall()
            conn.close()
            
            status = {}
            for row in rows:
                component, status_val, details = row
                status[component] = {
                    "status": status_val,
                    "details": json.loads(details) if details else None
                }
            
            # Default project status
            if not status:
                status = {
                    "ai_system": {
                        "status": "active",
                        "details": {
                            "azure_models": "configured",
                            "local_models": "disabled",
                            "embedding_system": "working"
                        }
                    },
                    "dataset_manager": {
                        "status": "disabled",
                        "details": {
                            "reason": "initialize method not implemented"
                        }
                    },
                    "api_endpoints": {
                        "status": "ready",
                        "details": {
                            "swagger_docs": "available",
                            "health_check": "working"
                        }
                    }
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error loading project status: {e}")
            return {}
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, preferences FROM user_preferences")
            rows = cursor.fetchall()
            conn.close()
            
            preferences = {}
            for row in rows:
                user_id, prefs_data = row
                preferences[user_id] = json.loads(prefs_data)
            
            # Default preferences
            if not preferences:
                preferences = {
                    "default": {
                        "writing_style": "neutral",
                        "preferred_models": ["gpt-4.1-mini", "claude-3-sonnet"],
                        "error_correction_style": "gentle",
                        "context_sensitivity": 0.7
                    }
                }
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            return {}
    
    def _load_available_tools(self) -> List[Dict[str, Any]]:
        """Load available tools from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT tool_name, tool_schema FROM available_tools WHERE is_active = 1")
            rows = cursor.fetchall()
            conn.close()
            
            tools = []
            for row in rows:
                tool_name, tool_schema = row
                tools.append({
                    "name": tool_name,
                    "schema": json.loads(tool_schema)
                })
            
            # Default tools
            if not tools:
                tools = [
                    {
                        "name": "file_reader",
                        "schema": {
                            "description": "Read file contents",
                            "parameters": {
                                "file_path": {"type": "string", "description": "Path to file"}
                            }
                        }
                    },
                    {
                        "name": "code_analyzer",
                        "schema": {
                            "description": "Analyze code structure",
                            "parameters": {
                                "code": {"type": "string", "description": "Code to analyze"}
                            }
                        }
                    }
                ]
            
            return tools
            
        except Exception as e:
            logger.error(f"Error loading available tools: {e}")
            return []
    
    def update_story_context(self, context_type: str, context_data: Dict[str, Any]):
        """Update story context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO story_context 
                (context_type, context_data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (context_type, json.dumps(context_data), now, now))
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            self.story_context[context_type] = context_data
            
            logger.info(f"Updated story context: {context_type}")
            
        except Exception as e:
            logger.error(f"Error updating story context: {e}")
    
    def update_project_status(self, component: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Update project status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO project_status 
                (component, status, details, last_updated)
                VALUES (?, ?, ?, ?)
            """, (component, status, json.dumps(details) if details else None, now))
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            self.project_status[component] = {
                "status": status,
                "details": details
            }
            
            logger.info(f"Updated project status: {component} = {status}")
            
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (user_id, preferences, last_updated)
                VALUES (?, ?, ?)
            """, (user_id, json.dumps(preferences), now))
            
            conn.commit()
            conn.close()
            
            # Update in-memory cache
            self.user_preferences[user_id] = preferences
            
            logger.info(f"Updated user preferences: {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
    
    def get_context_for_prompt(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get context data for prompt injection"""
        from src.core.prompt_templates import PromptContext
        
        user_prefs = None
        if user_id and user_id in self.user_preferences:
            user_prefs = self.user_preferences[user_id]
        elif "default" in self.user_preferences:
            user_prefs = self.user_preferences["default"]
        
        return PromptContext(
            story_context=self.story_context,
            project_status=self.project_status,
            user_preferences=user_prefs,
            available_tools=self.available_tools
        )

# Global instance
context_manager = ContextManager()
