"""
Inline Editor Integration API Routes

This module provides API endpoints for the Inline Editor Integration System.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from src.core.inline_editor_integration import (
    inline_editor_integration, EditorState, EditorSuggestion, EditorAction
)

router = APIRouter()

# Pydantic models for API requests/responses
class EditorStateRequest(BaseModel):
    """Request model for editor state updates"""
    current_text: str = Field(..., description="Current text in editor")
    cursor_position: int = Field(..., description="Current cursor position")
    selection_start: Optional[int] = Field(None, description="Selection start position")
    selection_end: Optional[int] = Field(None, description="Selection end position")
    file_path: Optional[str] = Field(None, description="Current file path")
    language: Optional[str] = Field(None, description="File language")

class EditorStateResponse(BaseModel):
    """Response model for editor state"""
    current_text: str
    cursor_position: int
    selection_start: Optional[int]
    selection_end: Optional[int]
    file_path: Optional[str]
    language: Optional[str]
    timestamp: datetime

class EditorSuggestionResponse(BaseModel):
    """Response model for editor suggestions"""
    id: str
    type: str
    text: str
    start_position: int
    end_position: int
    confidence: float
    reasoning: str
    priority: float
    metadata: Dict[str, Any]

class EditorActionResponse(BaseModel):
    """Response model for editor actions"""
    action_type: str
    text: str
    start_position: int
    end_position: int
    metadata: Dict[str, Any]

class WritingInsightsResponse(BaseModel):
    """Response model for writing insights"""
    text_length: int
    cursor_position: int
    writing_progress: float
    suggestions_available: int
    patterns_identified: int
    forecasts_generated: int
    strong_patterns: List[Dict[str, Any]]
    recent_forecasts: List[Dict[str, Any]]

@router.post("/update-state")
async def update_editor_state(request: EditorStateRequest):
    """Update the current editor state"""
    try:
        state = EditorState(
            current_text=request.current_text,
            cursor_position=request.cursor_position,
            selection_start=request.selection_start,
            selection_end=request.selection_end,
            file_path=request.file_path,
            language=request.language
        )
        
        await inline_editor_integration.update_editor_state(state)
        
        return {
            "message": "Editor state updated successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating editor state: {str(e)}")

@router.get("/suggestions", response_model=List[EditorSuggestionResponse])
async def get_suggestions(max_suggestions: int = 5):
    """Get current suggestions for the editor"""
    try:
        suggestions = await inline_editor_integration.get_suggestions(max_suggestions)
        
        response_suggestions = []
        for suggestion in suggestions:
            response_suggestions.append(EditorSuggestionResponse(
                id=suggestion.id,
                type=suggestion.type,
                text=suggestion.text,
                start_position=suggestion.start_position,
                end_position=suggestion.end_position,
                confidence=suggestion.confidence,
                reasoning=suggestion.reasoning,
                priority=suggestion.priority,
                metadata=suggestion.metadata
            ))
        
        return response_suggestions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")

@router.post("/apply-suggestion", response_model=EditorActionResponse)
async def apply_suggestion(suggestion_id: str):
    """Apply a suggestion and return the corresponding action"""
    try:
        action = await inline_editor_integration.apply_suggestion(suggestion_id)
        
        if not action:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        return EditorActionResponse(
            action_type=action.action_type,
            text=action.text,
            start_position=action.start_position,
            end_position=action.end_position,
            metadata=action.metadata
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying suggestion: {str(e)}")

@router.get("/predict-next-action", response_model=Optional[EditorActionResponse])
async def predict_next_action():
    """Predict the next likely editor action"""
    try:
        action = await inline_editor_integration.predict_next_action()
        
        if not action:
            return None
        
        return EditorActionResponse(
            action_type=action.action_type,
            text=action.text,
            start_position=action.start_position,
            end_position=action.end_position,
            metadata=action.metadata
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting next action: {str(e)}")

@router.get("/writing-insights", response_model=WritingInsightsResponse)
async def get_writing_insights():
    """Get insights about current writing session"""
    try:
        insights = await inline_editor_integration.get_writing_insights()
        
        return WritingInsightsResponse(**insights)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting writing insights: {str(e)}")

@router.get("/current-state", response_model=Optional[EditorStateResponse])
async def get_current_state():
    """Get the current editor state"""
    try:
        state = inline_editor_integration.current_state
        
        if not state:
            return None
        
        return EditorStateResponse(
            current_text=state.current_text,
            cursor_position=state.cursor_position,
            selection_start=state.selection_start,
            selection_end=state.selection_end,
            file_path=state.file_path,
            language=state.language,
            timestamp=state.timestamp
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting current state: {str(e)}")

@router.post("/batch-suggestions")
async def get_batch_suggestions(request: EditorStateRequest):
    """Get suggestions for a specific editor state without updating the current state"""
    try:
        # Create temporary state
        temp_state = EditorState(
            current_text=request.current_text,
            cursor_position=request.cursor_position,
            selection_start=request.selection_start,
            selection_end=request.selection_end,
            file_path=request.file_path,
            language=request.language
        )
        
        # Get suggestions for this state
        from src.core.agent_forecast import agent_forecast_system
        from src.core.context_manager import context_manager
        
        context = context_manager.get_context_for_prompt()
        story_context = {
            "current_text": temp_state.current_text,
            "cursor_position": temp_state.cursor_position,
            "file_path": temp_state.file_path,
            "language": temp_state.language,
            "story_context": context.story_context,
            "user_preferences": context.user_preferences
        }
        
        suggestions = await agent_forecast_system.get_context_aware_suggestions(
            temp_state.current_text,
            story_context
        )
        
        return {
            "suggestions": suggestions,
            "state": {
                "text_length": len(temp_state.current_text),
                "cursor_position": temp_state.cursor_position,
                "file_path": temp_state.file_path,
                "language": temp_state.language
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting batch suggestions: {str(e)}")

@router.get("/integration-status")
async def get_integration_status():
    """Get status of the integration system"""
    try:
        return inline_editor_integration.get_integration_status()
    
    except Exception as e:
        return {
            "system": "Inline Editor Integration",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/test-integration")
async def test_integration():
    """Test the integration system with sample data"""
    try:
        # Create test state
        test_state = EditorState(
            current_text="The hero stood at the edge of the cliff, looking down at the valley below.",
            cursor_position=45,
            file_path="test_story.md",
            language="markdown"
        )
        
        # Update state
        await inline_editor_integration.update_editor_state(test_state)
        
        # Get suggestions
        suggestions = await inline_editor_integration.get_suggestions(3)
        
        # Get insights
        insights = await inline_editor_integration.get_writing_insights()
        
        return {
            "test_completed": True,
            "suggestions_generated": len(suggestions),
            "insights_available": bool(insights),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "test_completed": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
