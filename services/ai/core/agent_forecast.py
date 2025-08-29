"""
Agent Forecast and Prediction System

This module implements intelligent forecasting and prediction capabilities
that integrate with the inline editor and context-aware data analysis.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
import numpy as np
from collections import defaultdict

from src.core.context_manager import context_manager
from src.core.prompt_templates import prompt_template_manager, PromptType
from src.core.model_router import model_router
from src.core.enhanced_ai_agents import enhanced_ai_agent_system, AIRequest, IntentType

logger = logging.getLogger(__name__)

class ForecastType(Enum):
    """Types of forecasts and predictions"""
    PLOT_DEVELOPMENT = "plot_development"      # การพัฒนาของโครงเรื่อง
    CHARACTER_ARC = "character_arc"            # การพัฒนาของตัวละคร
    SCENE_SEQUENCE = "scene_sequence"          # ลำดับฉาก
    READER_ENGAGEMENT = "reader_engagement"    # การมีส่วนร่วมของผู้อ่าน
    WRITING_PACE = "writing_pace"              # จังหวะการเขียน
    STORY_COMPLEXITY = "story_complexity"      # ความซับซ้อนของเรื่อง
    EMOTIONAL_JOURNEY = "emotional_journey"    # การเดินทางทางอารมณ์
    CONFLICT_RESOLUTION = "conflict_resolution" # การแก้ไขความขัดแย้ง

class PredictionConfidence(Enum):
    """Confidence levels for predictions"""
    HIGH = "high"      # 80-100%
    MEDIUM = "medium"  # 50-79%
    LOW = "low"        # 20-49%
    UNCERTAIN = "uncertain"  # <20%

@dataclass
class ForecastData:
    """Data structure for forecast information"""
    forecast_type: ForecastType
    current_value: float
    predicted_value: float
    confidence: PredictionConfidence
    timeframe: str  # e.g., "next_3_chapters", "next_week"
    factors: List[str]  # Factors influencing the prediction
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EditorPrediction:
    """Prediction for inline editor actions"""
    action_type: str  # "suggest_completion", "style_correction", "plot_hint"
    confidence: PredictionConfidence
    suggested_text: str
    reasoning: str
    context_sources: List[str]  # Sources of context used
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StoryPattern:
    """Identified patterns in the story"""
    pattern_type: str  # "character_development", "plot_structure", "pacing"
    strength: float  # 0-1, how strong the pattern is
    examples: List[str]  # Examples of this pattern
    implications: List[str]  # What this pattern suggests
    confidence: PredictionConfidence

class AgentForecastSystem:
    """Main system for agent forecasting and predictions"""
    
    def __init__(self, db_path: str = "forecast_data.db"):
        self.db_path = db_path
        self.patterns: Dict[str, StoryPattern] = {}
        self.forecasts: Dict[str, ForecastData] = {}
        self.editor_predictions: List[EditorPrediction] = []
        self._init_database()
        self._load_patterns()
    
    def _init_database(self):
        """Initialize forecast database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create forecasts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_type TEXT NOT NULL,
                current_value REAL NOT NULL,
                predicted_value REAL NOT NULL,
                confidence TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                factors TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Create editor predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editor_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                confidence TEXT NOT NULL,
                suggested_text TEXT NOT NULL,
                reasoning TEXT NOT NULL,
                context_sources TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Create story patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                strength REAL NOT NULL,
                examples TEXT NOT NULL,
                implications TEXT NOT NULL,
                confidence TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_patterns(self):
        """Load existing patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM story_patterns ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
        for row in rows:
            pattern = StoryPattern(
                pattern_type=row[1],
                strength=row[2],
                examples=json.loads(row[3]),
                implications=json.loads(row[4]),
                confidence=PredictionConfidence(row[5])
            )
            self.patterns[pattern.pattern_type] = pattern
        
        conn.close()
        logger.info(f"Loaded {len(self.patterns)} story patterns")
    
    async def analyze_story_patterns(self, story_context: Dict[str, Any]) -> List[StoryPattern]:
        """Analyze story context to identify patterns"""
        patterns = []
        
        try:
            # Get context for analysis
            context = context_manager.get_context_for_prompt()
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following story context and identify recurring patterns:
            
            Story Context:
            {json.dumps(story_context, indent=2, ensure_ascii=False)}
            
            User Preferences:
            {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
            
            Identify patterns in:
            1. Character development arcs
            2. Plot structure and pacing
            3. Conflict resolution patterns
            4. Emotional journey patterns
            5. Writing style consistency
            6. Theme development
            
            For each pattern, provide:
            - Pattern type
            - Strength (0-1)
            - Examples from the story
            - Implications for future development
            - Confidence level
            
            Respond in JSON format.
            """
            
            # Get AI analysis
            request = AIRequest(
                prompt=analysis_prompt,
                intent=IntentType.ANALYSIS,
                max_tokens=1000
            )
            
            response = await enhanced_ai_agent_system.process_request(request)
            
            # Parse response
            try:
                analysis_data = json.loads(response.content)
                for pattern_data in analysis_data.get("patterns", []):
                    pattern = StoryPattern(
                        pattern_type=pattern_data["type"],
                        strength=pattern_data["strength"],
                        examples=pattern_data["examples"],
                        implications=pattern_data["implications"],
                        confidence=PredictionConfidence(pattern_data["confidence"])
                    )
                    patterns.append(pattern)
                    self.patterns[pattern.pattern_type] = pattern
            except json.JSONDecodeError:
                logger.warning("Failed to parse pattern analysis response")
        
        except Exception as e:
            logger.error(f"Error analyzing story patterns: {e}")
        
        return patterns
    
    async def generate_forecast(self, forecast_type: ForecastType, 
                              story_context: Dict[str, Any]) -> ForecastData:
        """Generate forecast for a specific type"""
        
        try:
            # Get context
            context = context_manager.get_context_for_prompt()
            
            # Create forecast prompt
            forecast_prompt = f"""
            Generate a forecast for {forecast_type.value} based on the current story context:
            
            Story Context:
            {json.dumps(story_context, indent=2, ensure_ascii=False)}
            
            User Preferences:
            {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
            
            Current Patterns:
            {json.dumps([p.__dict__ for p in self.patterns.values()], indent=2, ensure_ascii=False)}
            
            Provide forecast for {forecast_type.value}:
            - Current value/state
            - Predicted value/state
            - Confidence level (high/medium/low/uncertain)
            - Timeframe for prediction
            - Key factors influencing the prediction
            
            Respond in JSON format.
            """
            
            # Get AI forecast
            request = AIRequest(
                prompt=forecast_prompt,
                intent=IntentType.ANALYSIS,
                max_tokens=500
            )
            
            response = await enhanced_ai_agent_system.process_request(request)
            
            # Parse response
            try:
                forecast_data = json.loads(response.content)
                
                forecast = ForecastData(
                    forecast_type=forecast_type,
                    current_value=forecast_data["current_value"],
                    predicted_value=forecast_data["predicted_value"],
                    confidence=PredictionConfidence(forecast_data["confidence"]),
                    timeframe=forecast_data["timeframe"],
                    factors=forecast_data["factors"],
                    timestamp=datetime.now(),
                    metadata=forecast_data.get("metadata", {})
                )
                
                # Save to database
                await self._save_forecast(forecast)
                
                return forecast
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse forecast response")
        
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
        
        # Return default forecast if analysis fails
        return ForecastData(
            forecast_type=forecast_type,
            current_value=0.0,
            predicted_value=0.0,
            confidence=PredictionConfidence.UNCERTAIN,
            timeframe="unknown",
            factors=["Analysis failed"],
            timestamp=datetime.now()
        )
    
    async def predict_editor_action(self, current_text: str, cursor_position: int,
                                  story_context: Dict[str, Any]) -> EditorPrediction:
        """Predict next editor action based on current context"""
        
        try:
            # Get context
            context = context_manager.get_context_for_prompt()
            
            # Create prediction prompt
            prediction_prompt = f"""
            Predict the next editor action based on current writing context:
            
            Current Text (around cursor):
            {current_text[:cursor_position]}|{current_text[cursor_position:]}
            
            Cursor Position: {cursor_position}
            
            Story Context:
            {json.dumps(story_context, indent=2, ensure_ascii=False)}
            
            User Preferences:
            {json.dumps(context.user_preferences, indent=2, ensure_ascii=False)}
            
            Current Patterns:
            {json.dumps([p.__dict__ for p in self.patterns.values()], indent=2, ensure_ascii=False)}
            
            Predict:
            - Action type (suggest_completion, style_correction, plot_hint, character_development)
            - Suggested text to insert/change
            - Reasoning for the suggestion
            - Confidence level
            - Context sources used
            
            Respond in JSON format.
            """
            
            # Get AI prediction
            request = AIRequest(
                prompt=prediction_prompt,
                intent=IntentType.CREATIVE_WRITING,
                max_tokens=300
            )
            
            response = await enhanced_ai_agent_system.process_request(request)
            
            # Parse response
            try:
                prediction_data = json.loads(response.content)
                
                prediction = EditorPrediction(
                    action_type=prediction_data["action_type"],
                    confidence=PredictionConfidence(prediction_data["confidence"]),
                    suggested_text=prediction_data["suggested_text"],
                    reasoning=prediction_data["reasoning"],
                    context_sources=prediction_data["context_sources"],
                    timestamp=datetime.now(),
                    metadata=prediction_data.get("metadata", {})
                )
                
                # Save to database
                await self._save_editor_prediction(prediction)
                
                return prediction
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse editor prediction response")
        
        except Exception as e:
            logger.error(f"Error predicting editor action: {e}")
        
        # Return default prediction if analysis fails
        return EditorPrediction(
            action_type="suggest_completion",
            confidence=PredictionConfidence.UNCERTAIN,
            suggested_text="",
            reasoning="Analysis failed",
            context_sources=[],
            timestamp=datetime.now()
        )
    
    async def get_context_aware_suggestions(self, current_text: str, 
                                          story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get context-aware suggestions for the current writing position"""
        
        suggestions = []
        
        try:
            # Analyze current text and context
            context = context_manager.get_context_for_prompt()
            
            # Get patterns
            patterns = await self.analyze_story_patterns(story_context)
            
            # Generate suggestions based on patterns
            for pattern in patterns:
                if pattern.strength > 0.6:  # Only use strong patterns
                    suggestion = {
                        "type": f"pattern_based_{pattern.pattern_type}",
                        "text": self._generate_pattern_suggestion(pattern, current_text),
                        "confidence": pattern.confidence.value,
                        "reasoning": f"Based on strong {pattern.pattern_type} pattern",
                        "priority": pattern.strength
                    }
                    suggestions.append(suggestion)
            
            # Get AI-generated suggestions
            ai_suggestion = await self.predict_editor_action(current_text, len(current_text), story_context)
            if ai_suggestion.confidence != PredictionConfidence.UNCERTAIN:
                suggestions.append({
                    "type": ai_suggestion.action_type,
                    "text": ai_suggestion.suggested_text,
                    "confidence": ai_suggestion.confidence.value,
                    "reasoning": ai_suggestion.reasoning,
                    "priority": 0.8
                })
            
            # Sort by priority
            suggestions.sort(key=lambda x: x["priority"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting context-aware suggestions: {e}")
        
        return suggestions
    
    def _generate_pattern_suggestion(self, pattern: StoryPattern, current_text: str) -> str:
        """Generate suggestion text based on pattern"""
        
        if pattern.pattern_type == "character_development":
            return "Consider developing this character's arc further based on established patterns."
        elif pattern.pattern_type == "plot_structure":
            return "This plot point follows your established structure. Consider the next logical step."
        elif pattern.pattern_type == "pacing":
            return "The pacing here matches your typical rhythm. Consider maintaining this flow."
        elif pattern.pattern_type == "conflict_resolution":
            return "This conflict resolution follows your established pattern. Consider the implications."
        else:
            return f"Consider how this relates to your {pattern.pattern_type} pattern."
    
    async def _save_forecast(self, forecast: ForecastData):
        """Save forecast to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO forecasts
            (forecast_type, current_value, predicted_value, confidence,
             timeframe, factors, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            forecast.forecast_type.value,
            forecast.current_value,
            forecast.predicted_value,
            forecast.confidence.value,
            forecast.timeframe,
            json.dumps(forecast.factors),
            forecast.timestamp.isoformat(),
            json.dumps(forecast.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    async def _save_editor_prediction(self, prediction: EditorPrediction):
        """Save editor prediction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO editor_predictions
            (action_type, confidence, suggested_text, reasoning,
             context_sources, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction.action_type,
            prediction.confidence.value,
            prediction.suggested_text,
            prediction.reasoning,
            json.dumps(prediction.context_sources),
            prediction.timestamp.isoformat(),
            json.dumps(prediction.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get summary of all forecasts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT forecast_type, predicted_value, confidence, timestamp
            FROM forecasts
            WHERE timestamp = (
                SELECT MAX(timestamp)
                FROM forecasts f2
                WHERE f2.forecast_type = forecasts.forecast_type
            )
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        summary = {
            "total_forecasts": len(rows),
            "forecasts": []
        }
        
        for row in rows:
            forecast_type, predicted_value, confidence, timestamp = row
            summary["forecasts"].append({
                "type": forecast_type,
                "predicted_value": predicted_value,
                "confidence": confidence,
                "timestamp": timestamp
            })
        
        return summary

# Global instance
agent_forecast_system = AgentForecastSystem()
