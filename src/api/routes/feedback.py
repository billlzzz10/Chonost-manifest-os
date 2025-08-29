"""
Feedback API routes for Chonost

This module provides feedback loop endpoints including:
- User feedback collection
- Error correction learning
- Performance tracking
- System improvement
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from src.core.enhanced_ai_agents import (
    enhanced_ai_agent_system, ErrorType, ErrorContext, UserPreference
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models

class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    original_request: str
    ai_response: str
    user_feedback: str
    rating: int  # 1-5 scale
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    model_used: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ErrorCorrectionRequest(BaseModel):
    """Request model for error correction"""
    original_text: str
    corrected_text: str
    error_type: str
    context: Dict[str, Any]
    user_feedback: Optional[str] = None
    model_used: str
    confidence: float
    user_id: Optional[str] = None

class UserPreferenceRequest(BaseModel):
    """Request model for user preferences"""
    user_id: str
    writing_style: str = "neutral"
    preferred_models: List[str] = []
    error_correction_style: str = "gentle"
    context_sensitivity: float = 0.7
    learning_rate: float = 0.1

class FeedbackResponse(BaseModel):
    """Response model for feedback"""
    feedback_id: str
    status: str
    message: str
    improvements_suggested: List[str]
    learning_applied: bool

class FeedbackAnalysisResponse(BaseModel):
    """Response model for feedback analysis"""
    total_feedback: int
    average_rating: float
    common_issues: List[Dict[str, Any]]
    improvement_suggestions: List[str]
    system_health_score: float

# API Endpoints

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for AI response"""
    try:
        # Validate rating
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Generate feedback ID
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.user_feedback) % 10000}"
        
        # Process feedback through AI system
        feedback_data = {
            "original_request": request.original_request,
            "ai_response": request.ai_response,
            "user_feedback": request.user_feedback,
            "rating": request.rating,
            "user_id": request.user_id,
            "project_id": request.project_id,
            "model_used": request.model_used,
            "context": request.context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Apply learning if rating is low
        learning_applied = False
        improvements_suggested = []
        
        if request.rating <= 3:
            # Trigger learning process
            try:
                await enhanced_ai_agent_system.learn_from_feedback(feedback_data)
                learning_applied = True
                improvements_suggested = [
                    "System has learned from your feedback",
                    "Similar requests will be improved",
                    "Model selection may be adjusted"
                ]
            except Exception as e:
                logger.warning(f"Learning from feedback failed: {e}")
                improvements_suggested = ["Feedback recorded for future analysis"]
        else:
            improvements_suggested = ["Thank you for the positive feedback!"]
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message="Feedback submitted successfully",
            improvements_suggested=improvements_suggested,
            learning_applied=learning_applied
        )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/error-correction", response_model=FeedbackResponse)
async def submit_error_correction(request: ErrorCorrectionRequest):
    """Submit error correction for learning"""
    try:
        # Create error context
        error_context = ErrorContext(
            original_text=request.original_text,
            corrected_text=request.corrected_text,
            error_type=ErrorType(request.error_type),
            context=request.context,
            user_feedback=request.user_feedback,
            model_used=request.model_used,
            confidence=request.confidence,
            user_id=request.user_id,
            timestamp=datetime.now()
        )
        
        # Process error correction
        feedback_id = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.corrected_text) % 10000}"
        
        # Apply learning
        try:
            await enhanced_ai_agent_system.learn_from_error(error_context)
            learning_applied = True
            improvements_suggested = [
                "Error correction learned",
                "Similar errors will be prevented",
                "Model confidence adjusted"
            ]
        except Exception as e:
            logger.warning(f"Learning from error failed: {e}")
            learning_applied = False
            improvements_suggested = ["Error correction recorded for analysis"]
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message="Error correction submitted successfully",
            improvements_suggested=improvements_suggested,
            learning_applied=learning_applied
        )
        
    except Exception as e:
        logger.error(f"Error submitting error correction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-preferences", response_model=FeedbackResponse)
async def update_user_preferences(request: UserPreferenceRequest):
    """Update user preferences for personalization"""
    try:
        # Create user preference
        user_preference = UserPreference(
            user_id=request.user_id,
            writing_style=request.writing_style,
            preferred_models=request.preferred_models,
            error_correction_style=request.error_correction_style,
            context_sensitivity=request.context_sensitivity,
            learning_rate=request.learning_rate,
            timestamp=datetime.now()
        )
        
        # Update preferences in AI system
        await enhanced_ai_agent_system.update_user_preferences(user_preference)
        
        feedback_id = f"pref_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.user_id) % 10000}"
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="success",
            message="User preferences updated successfully",
            improvements_suggested=[
                "Personalization applied",
                "Future responses will be tailored",
                "Model selection optimized for your preferences"
            ],
            learning_applied=True
        )
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis", response_model=FeedbackAnalysisResponse)
async def get_feedback_analysis():
    """Get feedback analysis and system health"""
    try:
        # Get feedback statistics from AI system
        feedback_stats = await enhanced_ai_agent_system.get_feedback_statistics()
        
        # Calculate system health score
        total_feedback = feedback_stats.get("total_feedback", 0)
        average_rating = feedback_stats.get("average_rating", 0.0)
        common_issues = feedback_stats.get("common_issues", [])
        
        # Calculate health score based on average rating
        if total_feedback > 0:
            health_score = min(100.0, (average_rating / 5.0) * 100.0)
        else:
            health_score = 100.0  # Default to perfect if no feedback
        
        # Generate improvement suggestions
        improvement_suggestions = []
        if average_rating < 4.0:
            improvement_suggestions.append("Consider adjusting model selection criteria")
        if len(common_issues) > 0:
            improvement_suggestions.append("Address common user feedback patterns")
        if health_score < 80.0:
            improvement_suggestions.append("System performance needs attention")
        
        return FeedbackAnalysisResponse(
            total_feedback=total_feedback,
            average_rating=average_rating,
            common_issues=common_issues,
            improvement_suggestions=improvement_suggestions,
            system_health_score=health_score
        )
        
    except Exception as e:
        logger.error(f"Error getting feedback analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    try:
        preferences = await enhanced_ai_agent_system.get_user_preferences(user_id)
        
        if preferences:
            return {
                "user_id": user_id,
                "preferences": preferences.dict(),
                "last_updated": preferences.timestamp.isoformat()
            }
        else:
            return {
                "user_id": user_id,
                "preferences": None,
                "message": "No preferences found for this user"
            }
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user-preferences/{user_id}")
async def delete_user_preferences(user_id: str):
    """Delete user preferences"""
    try:
        await enhanced_ai_agent_system.delete_user_preferences(user_id)
        
        return {
            "user_id": user_id,
            "status": "success",
            "message": "User preferences deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def feedback_system_health():
    """Check feedback system health"""
    try:
        # Test feedback system functionality
        test_feedback = {
            "original_request": "Test request",
            "ai_response": "Test response",
            "user_feedback": "Test feedback",
            "rating": 5,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if feedback can be processed
        can_process = await enhanced_ai_agent_system.can_process_feedback(test_feedback)
        
        return {
            "status": "healthy" if can_process else "degraded",
            "feedback_system_available": can_process,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Feedback system health check failed: {e}")
        return {
            "status": "unhealthy",
            "feedback_system_available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
