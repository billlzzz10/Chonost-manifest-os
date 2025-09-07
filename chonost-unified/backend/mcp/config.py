"""
Configuration settings สำหรับ MCP Orchestrator
"""

import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    """Application settings"""
    
    # Logging
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Log level for the application"
    )
    
    # MCP Pool Settings
    mcp_ttl_seconds: int = Field(
        default=int(os.getenv("MCP_TTL_SECONDS", "300")),
        description="Time to live for MCP connections in seconds"
    )
    
    mcp_pool_max: int = Field(
        default=int(os.getenv("MCP_POOL_MAX", "4")),
        description="Maximum number of MCP connections in pool"
    )
    
    # Server Settings
    host: str = Field(
        default=os.getenv("HOST", "0.0.0.0"),
        description="Host to bind the server to"
    )
    
    port: int = Field(
        default=int(os.getenv("PORT", "8000")),
        description="Port to bind the server to"
    )
    
    # Environment
    environment: str = Field(
        default=os.getenv("ENVIRONMENT", "development"),
        description="Environment (development, staging, production)"
    )
    
    # Debug mode
    debug: bool = Field(
        default=os.getenv("DEBUG", "false").lower() == "true",
        description="Enable debug mode"
    )

# Global settings instance
settings = Settings()

# Environment-specific overrides
if settings.environment == "production":
    settings.debug = False
    settings.log_level = "WARNING"
elif settings.environment == "staging":
    settings.debug = False
    settings.log_level = "INFO"
