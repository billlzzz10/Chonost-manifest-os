"""
AI Routes - AI Provider Management and Integration

This module provides endpoints for managing AI providers, completions, and integrations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import os

from jose import JWTError, jwt

# Import services
try:
    from src.services.ai_orchestrator import AIOrchestrator
except ImportError:
    # Fallback imports
    class AIOrchestrator:
        pass

# Security
security = HTTPBearer()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable must be set")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Pydantic models
class ProviderConfig(BaseModel):
    provider: str = Field(..., description="AI provider name")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Base URL for the provider")
    model: Optional[str] = Field(None, description="Default model for the provider")
    config: Optional[Dict[str, Any]] = Field({}, description="Additional configuration")

class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt")
    model: Optional[str] = Field(None, description="Model to use")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens")
    temperature: Optional[float] = Field(0.7, description="Temperature")
    stream: Optional[bool] = Field(False, description="Stream response")
    config: Optional[Dict[str, Any]] = Field({}, description="Additional configuration")

class CompletionResponse(BaseModel):
    id: str
    provider: str
    model: str
    content: str
    usage: Dict[str, Any]
    created_at: datetime

class ContentAnalysisRequest(BaseModel):
    content: str = Field(..., description="Content to analyze")
    analysis_type: str = Field(..., description="Type of analysis")
    config: Optional[Dict[str, Any]] = Field({}, description="Analysis configuration")

class IntegrationConfig(BaseModel):
    service: str = Field(..., description="Integration service name")
    config: Dict[str, Any] = Field(..., description="Integration configuration")

class MCPToolRequest(BaseModel):
    tool_name: str = Field(..., description="MCP tool name")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")

# Create router
router = APIRouter(prefix="/ai", tags=["ai"])

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return {"id": user_id}

# Initialize AI Orchestrator
ai_orchestrator = AIOrchestrator()

# Provider Management
@router.post("/providers")
async def configure_provider(
    config: ProviderConfig,
    current_user: dict = Depends(get_current_user)
):
    """Configure an AI provider"""
    try:
        result = ai_orchestrator.configure_provider(
            user_id=current_user["id"],
            provider=config.provider,
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            config=config.config
        )
        
        if result["success"]:
            return {"message": "Provider configured successfully", "provider": config.provider}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.get("/providers")
async def list_providers(current_user: dict = Depends(get_current_user)):
    """List configured AI providers"""
    try:
        result = ai_orchestrator.list_providers(user_id=current_user["id"])
        
        if result["success"]:
            return result["providers"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.delete("/providers/{provider}")
async def remove_provider(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove an AI provider"""
    try:
        result = ai_orchestrator.remove_provider(
            user_id=current_user["id"],
            provider=provider
        )
        
        if result["success"]:
            return {"message": f"Provider {provider} removed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.post("/providers/{provider}/test")
async def test_provider(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Test AI provider connection"""
    try:
        result = ai_orchestrator.test_provider(
            user_id=current_user["id"],
            provider=provider
        )
        
        if result["success"]:
            return {"message": "Provider test successful", "details": result["details"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

# Completions
@router.post("/completions", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a completion using AI providers"""
    try:
        result = ai_orchestrator.create_completion(
            user_id=current_user["id"],
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream,
            config=request.config
        )
        
        if result["success"]:
            return CompletionResponse(
                id=str(uuid.uuid4()),
                provider=result["provider"],
                model=result["model"],
                content=result["content"],
                usage=result["usage"],
                created_at=datetime.utcnow()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.post("/completions/stream")
async def create_streaming_completion(
    request: CompletionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a streaming completion"""
    try:
        # Set stream to True
        request.stream = True
        
        result = ai_orchestrator.create_completion(
            user_id=current_user["id"],
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=True,
            config=request.config
        )
        
        if result["success"]:
            return result["stream"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

# Content Analysis
@router.post("/analyze")
async def analyze_content(
    request: ContentAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze content using AI"""
    try:
        result = ai_orchestrator.analyze_content(
            user_id=current_user["id"],
            content=request.content,
            analysis_type=request.analysis_type,
            config=request.config
        )
        
        if result["success"]:
            return result["analysis"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

# Integrations
@router.post("/integrations")
async def configure_integration(
    config: IntegrationConfig,
    current_user: dict = Depends(get_current_user)
):
    """Configure external integration"""
    try:
        result = ai_orchestrator.configure_integration(
            user_id=current_user["id"],
            service=config.service,
            config=config.config
        )
        
        if result["success"]:
            return {"message": f"Integration {config.service} configured successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.get("/integrations")
async def list_integrations(current_user: dict = Depends(get_current_user)):
    """List configured integrations"""
    try:
        result = ai_orchestrator.list_integrations(user_id=current_user["id"])
        
        if result["success"]:
            return result["integrations"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

# MCP Tools
@router.get("/mcp/tools")
async def list_mcp_tools(current_user: dict = Depends(get_current_user)):
    """List available MCP tools"""
    try:
        result = ai_orchestrator.list_mcp_tools(user_id=current_user["id"])
        
        if result["success"]:
            return result["tools"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.post("/mcp/tools/execute")
async def execute_mcp_tool(
    request: MCPToolRequest,
    current_user: dict = Depends(get_current_user)
):
    """Execute an MCP tool"""
    try:
        result = ai_orchestrator.execute_mcp_tool(
            user_id=current_user["id"],
            tool_name=request.tool_name,
            parameters=request.parameters
        )
        
        if result["success"]:
            return result["result"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

# Analytics
@router.get("/analytics/usage")
async def get_usage_analytics(current_user: dict = Depends(get_current_user)):
    """Get usage analytics"""
    try:
        result = ai_orchestrator.get_usage_analytics(user_id=current_user["id"])
        
        if result["success"]:
            return result["analytics"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )

@router.get("/analytics/costs")
async def get_cost_analytics(current_user: dict = Depends(get_current_user)):
    """Get cost analytics"""
    try:
        result = ai_orchestrator.get_cost_analytics(user_id=current_user["id"])
        
        if result["success"]:
            return result["costs"]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาด: {str(e)}"
        )
