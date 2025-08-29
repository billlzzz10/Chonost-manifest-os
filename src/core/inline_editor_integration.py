"""
Inline Editor Integration System

This module provides integration between the inline editor and the Agent Forecast System,
enabling context-aware suggestions and predictions during writing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import sqlite3

from src.core.agent_forecast import agent_forecast_system, ForecastType, PredictionConfidence
from src.core.context_manager import context_manager
from src.core.enhanced_ai_agents import enhanced_ai_agent_system, AIRequest, IntentType

logger = logging.getLogger(__name__)

@dataclass
class EditorState:
    """Current state of the inline editor"""
    current_text: str
    cursor_position: int
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    file_path: Optional[str] = None
    language: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EditorSuggestion:
    """Suggestion for the inline editor"""
    id: str
    type: str  # "completion", "correction", "enhancement", "prediction"
    text: str
    start_position: int
    end_position: int
    confidence: float
    reasoning: str
    priority: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EditorAction:
    """Action to be performed in the editor"""
    action_type: str  # "insert", "replace", "delete", "format"
    text: str
    start_position: int
    end_position: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class InlineEditorIntegration:
    """Main integration system for inline editor"""
    
    def __init__(self, db_path: str = "editor_integration.db"):
        self.db_path = db_path
        self.current_state: Optional[EditorState] = None
        self.suggestions: List[EditorSuggestion] = []
        self.actions: List[EditorAction] = []
        self._init_database()
    
    def _init_database(self):
        """Initialize editor integration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create editor states table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editor_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_text TEXT NOT NULL,
                cursor_position INTEGER NOT NULL,
                selection_start INTEGER,
                selection_end INTEGER,
                file_path TEXT,
                language TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create editor suggestions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editor_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_id TEXT NOT NULL,
                type TEXT NOT NULL,
                text TEXT NOT NULL,
                start_position INTEGER NOT NULL,
                end_position INTEGER NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT NOT NULL,
                priority REAL NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create editor actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editor_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                text TEXT NOT NULL,
                start_position INTEGER NOT NULL,
                end_position INTEGER NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def update_editor_state(self, state: EditorState) -> None:
        """Update the current editor state"""
        self.current_state = state
        await self._save_editor_state(state)
        
        # Trigger context-aware analysis
        await self._analyze_current_context()
    
    async def _analyze_current_context(self) -> None:
        """Analyze current editor context and generate suggestions"""
        if not self.current_state:
            return
        
        try:
            # Get story context (fast operation)
            context = context_manager.get_context_for_prompt()
            story_context = {
                "current_text": self.current_state.current_text,
                "cursor_position": self.current_state.cursor_position,
                "file_path": self.current_state.file_path,
                "language": self.current_state.language,
                "story_context": context.story_context,
                "user_preferences": context.user_preferences
            }
            
            # Generate simple suggestions without AI calls (fast)
            suggestions = self._generate_fast_suggestions(story_context)
            
            # Convert to EditorSuggestion objects
            self.suggestions = []
            for i, suggestion in enumerate(suggestions):
                editor_suggestion = EditorSuggestion(
                    id=f"suggestion_{i}_{datetime.now().timestamp()}",
                    type=suggestion["type"],
                    text=suggestion["text"],
                    start_position=self.current_state.cursor_position,
                    end_position=self.current_state.cursor_position,
                    confidence=float(suggestion["confidence"]),
                    reasoning=suggestion["reasoning"],
                    priority=suggestion["priority"],
                    metadata={"source": "fast_analysis"}
                )
                self.suggestions.append(editor_suggestion)
            
            # Save suggestions (async, don't wait)
            asyncio.create_task(self._save_suggestions(self.suggestions))
            
        except Exception as e:
            logger.error(f"Error analyzing current context: {e}")
    
    def _generate_fast_suggestions(self, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fast suggestions without AI calls"""
        suggestions = []
        
        # Simple text-based suggestions
        current_text = story_context.get("current_text", "")
        cursor_pos = story_context.get("cursor_position", 0)
        
        # Check for incomplete sentences
        if current_text and not current_text.rstrip().endswith(('.', '!', '?')):
            suggestions.append({
                "type": "completion",
                "text": "Consider completing this sentence.",
                "confidence": 0.7,
                "reasoning": "Incomplete sentence detected",
                "priority": 0.6
            })
        
        # Check for paragraph length
        paragraphs = current_text.split('\n\n')
        if paragraphs and len(paragraphs[-1]) > 500:
            suggestions.append({
                "type": "structure",
                "text": "Consider breaking this paragraph for better readability.",
                "confidence": 0.8,
                "reasoning": "Long paragraph detected",
                "priority": 0.7
            })
        
        # Check for repetitive words
        words = current_text.lower().split()
        if len(words) > 10:
            word_counts = {}
            for word in words[-20:]:  # Check last 20 words
                if len(word) > 3:  # Only count words longer than 3 characters
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            repetitive_words = [word for word, count in word_counts.items() if count > 2]
            if repetitive_words:
                suggestions.append({
                    "type": "style",
                    "text": f"Consider varying your word choice. '{repetitive_words[0]}' appears frequently.",
                    "confidence": 0.6,
                    "reasoning": "Repetitive word usage detected",
                    "priority": 0.5
                })
        
        return suggestions
    
    async def get_suggestions(self, max_suggestions: int = 5) -> List[EditorSuggestion]:
        """Get current suggestions for the editor"""
        # Sort by priority and confidence
        sorted_suggestions = sorted(
            self.suggestions,
            key=lambda x: (x.priority, x.confidence),
            reverse=True
        )
        
        return sorted_suggestions[:max_suggestions]
    
    async def apply_suggestion(self, suggestion_id: str) -> Optional[EditorAction]:
        """Apply a suggestion and return the corresponding action"""
        suggestion = next((s for s in self.suggestions if s.id == suggestion_id), None)
        if not suggestion:
            return None
        
        # Create action based on suggestion type
        if suggestion.type == "suggest_completion":
            action = EditorAction(
                action_type="insert",
                text=suggestion.text,
                start_position=suggestion.start_position,
                end_position=suggestion.end_position,
                metadata={"suggestion_id": suggestion_id, "confidence": suggestion.confidence}
            )
        elif suggestion.type == "style_correction":
            action = EditorAction(
                action_type="replace",
                text=suggestion.text,
                start_position=suggestion.start_position,
                end_position=suggestion.end_position,
                metadata={"suggestion_id": suggestion_id, "confidence": suggestion.confidence}
            )
        else:
            action = EditorAction(
                action_type="insert",
                text=suggestion.text,
                start_position=suggestion.start_position,
                end_position=suggestion.end_position,
                metadata={"suggestion_id": suggestion_id, "confidence": suggestion.confidence}
            )
        
        # Save action
        await self._save_action(action)
        
        return action
    
    async def predict_next_action(self) -> Optional[EditorAction]:
        """Predict the next likely editor action"""
        if not self.current_state:
            return None
        
        try:
            # Get story context
            context = context_manager.get_context_for_prompt()
            story_context = {
                "current_text": self.current_state.current_text,
                "cursor_position": self.current_state.cursor_position,
                "file_path": self.current_state.file_path,
                "story_context": context.story_context,
                "user_preferences": context.user_preferences
            }
            
            # Get prediction from forecast system
            prediction = await agent_forecast_system.predict_editor_action(
                self.current_state.current_text,
                self.current_state.cursor_position,
                story_context
            )
            
            if prediction.confidence == PredictionConfidence.UNCERTAIN:
                return None
            
            # Create action based on prediction
            action = EditorAction(
                action_type="insert",
                text=prediction.suggested_text,
                start_position=self.current_state.cursor_position,
                end_position=self.current_state.cursor_position,
                metadata={
                    "prediction_type": prediction.action_type,
                    "confidence": prediction.confidence.value,
                    "reasoning": prediction.reasoning
                }
            )
            
            return action
            
        except Exception as e:
            logger.error(f"Error predicting next action: {e}")
            return None
    
    async def get_writing_insights(self) -> Dict[str, Any]:
        """Get insights about current writing session"""
        if not self.current_state:
            return {}
        
        try:
            # Get story context
            context = context_manager.get_context_for_prompt()
            story_context = {
                "current_text": self.current_state.current_text,
                "cursor_position": self.current_state.cursor_position,
                "story_context": context.story_context,
                "user_preferences": context.user_preferences
            }
            
            insights = {
                "text_length": len(self.current_state.current_text),
                "cursor_position": self.current_state.cursor_position,
                "writing_progress": self.current_state.cursor_position / max(len(self.current_state.current_text), 1),
                "suggestions_available": len(self.suggestions),
                "patterns_identified": len(agent_forecast_system.patterns),
                "forecasts_generated": len(agent_forecast_system.forecasts)
            }
            
            # Get pattern insights
            pattern_insights = []
            for pattern in agent_forecast_system.patterns.values():
                if pattern.strength > 0.7:  # Only strong patterns
                    pattern_insights.append({
                        "type": pattern.pattern_type,
                        "strength": pattern.strength,
                        "implications": pattern.implications[:2]  # First 2 implications
                    })
            
            insights["strong_patterns"] = pattern_insights
            
            # Get forecast insights
            forecast_summary = agent_forecast_system.get_forecast_summary()
            insights["recent_forecasts"] = forecast_summary["forecasts"][:3]  # Last 3 forecasts
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting writing insights: {e}")
            return {}
    
    async def _save_editor_state(self, state: EditorState) -> None:
        """Save editor state to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO editor_states
            (current_text, cursor_position, selection_start, selection_end,
             file_path, language, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            state.current_text,
            state.cursor_position,
            state.selection_start,
            state.selection_end,
            state.file_path,
            state.language,
            state.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_suggestions(self, suggestions: List[EditorSuggestion]) -> None:
        """Save suggestions to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for suggestion in suggestions:
            cursor.execute("""
                INSERT INTO editor_suggestions
                (suggestion_id, type, text, start_position, end_position,
                 confidence, reasoning, priority, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                suggestion.id,
                suggestion.type,
                suggestion.text,
                suggestion.start_position,
                suggestion.end_position,
                suggestion.confidence,
                suggestion.reasoning,
                suggestion.priority,
                json.dumps(suggestion.metadata),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    async def _save_action(self, action: EditorAction) -> None:
        """Save action to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO editor_actions
            (action_type, text, start_position, end_position, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            action.action_type,
            action.text,
            action.start_position,
            action.end_position,
            json.dumps(action.metadata),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of the integration system"""
        return {
            "system": "Inline Editor Integration",
            "status": "operational",
            "current_state": self.current_state is not None,
            "suggestions_count": len(self.suggestions),
            "actions_count": len(self.actions),
            "database_path": self.db_path,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
inline_editor_integration = InlineEditorIntegration()
