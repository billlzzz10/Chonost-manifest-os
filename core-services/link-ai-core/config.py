"""
Configuration settings for the MCP Orchestrator.
"""

import os
from pydantic import BaseModel, Field
from typing import Optional

class Settings(BaseModel):
    """
    Application settings.

    Attributes:
        log_level (str): The log level for the application.
        mcp_ttl_seconds (int): The time-to-live for MCP connections in seconds.
        mcp_pool_max (int): The maximum number of MCP connections in the pool.
        host (str): The host to bind the server to.
        port (int): The port to bind the server to.
        environment (str): The environment (development, staging, production).
        debug (bool): A flag indicating whether to enable debug mode.
        database_url (str): The database connection string.
        db_echo_log (bool): A flag indicating whether to echo database logs.
    """
    
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

    # Database Settings
    database_url: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./chonost_manuscript.db"),
        description="Database connection string"
    )
    db_echo_log: bool = Field(
        default=os.getenv("DB_ECHO_LOG", "false").lower() == "true",
        description="Echo database logs"
    )

    # AI Provider API Keys
    openai_api_key: Optional[str] = Field(default=os.getenv("OPENAI_API_KEY"), description="API key for OpenAI")
    anthropic_api_key: Optional[str] = Field(default=os.getenv("ANTHROPIC_API_KEY"), description="API key for Anthropic")
    google_api_key: Optional[str] = Field(default=os.getenv("GOOGLE_API_KEY"), description="API key for Google AI")
    mistral_api_key: Optional[str] = Field(default=os.getenv("MISTRAL_API_KEY"), description="API key for Mistral AI")
    openrouter_api_key: Optional[str] = Field(default=os.getenv("OPENROUTER_API_KEY"), description="API key for OpenRouter")
    deepseek_api_key: Optional[str] = Field(default=os.getenv("DEEPSEEK_API_KEY"), description="API key for DeepSeek")

# Global settings instance
settings = Settings()

# Environment-specific overrides
if settings.environment == "production":
    settings.debug = False
    settings.log_level = "WARNING"
elif settings.environment == "staging":
    settings.debug = False
    settings.log_level = "INFO"
