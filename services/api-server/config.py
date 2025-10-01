"""
Configuration settings for the MCP Orchestrator.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


def _env_bool(name: str, default: bool) -> bool:
    """Return a boolean environment variable with a safe fallback."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    """
    Application settings for the API server and orchestrator runtime.

    Attributes:
        log_level: Log level for application output.
        mcp_ttl_seconds: Lifetime for pooled MCP connections.
        mcp_pool_max: Maximum size of the MCP connection pool.
        host: Hostname/IP the FastAPI server binds to.
        port: Port the FastAPI server listens on.
        reload: Flag to enable auto-reload (usually in development).
        environment: Deployment environment name.
        debug: Toggle for debug behaviours in downstream components.
        database_url: Primary database connection string.
        redis_url: Redis cache connection string.
        qdrant_url: Qdrant vector database endpoint.
        jwt_secret: Shared secret for JWT validation.
        openai_api_key: API key for OpenAI integrations.
        anthropic_api_key: API key for Anthropic integrations.
        google_api_key: API key for Google AI integrations.
        mistral_api_key: API key for Mistral integrations.
        openrouter_api_key: API key for OpenRouter integrations.
        deepseek_api_key: API key for DeepSeek integrations.
    """

    # Logging
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Log level for the application",
    )

    # MCP Pool Settings
    mcp_ttl_seconds: int = Field(
        default=int(os.getenv("MCP_TTL_SECONDS", "300")),
        description="Time to live for MCP connections in seconds",
    )

    mcp_pool_max: int = Field(
        default=int(os.getenv("MCP_POOL_MAX", "4")),
        description="Maximum number of MCP connections in pool",
    )

    # Server Settings
    host: str = Field(
        default=os.getenv("API_HOST", os.getenv("HOST", "0.0.0.0")),
        description="Host to bind the server to",
    )

    port: int = Field(
        default=int(
            os.getenv("API_PORT", os.getenv("PORT", "8000"))
        ),
        description="Port to bind the server to",
    )

    reload: bool = Field(
        default=_env_bool("API_RELOAD", True),
        description="Enable auto-reload for development",
    )

    # Environment
    environment: str = Field(
        default=os.getenv("ENVIRONMENT", "development"),
        description="Environment (development, staging, production)",
    )

    # Debug mode
    debug: bool = Field(
        default=_env_bool("DEBUG", False),
        description="Enable debug mode",
    )

    # Service URLs / Secrets
    database_url: Optional[str] = Field(
        default=os.getenv("DATABASE_URL"),
        description="Database connection string",
    )
    redis_url: Optional[str] = Field(
        default=os.getenv("REDIS_URL"),
        description="Redis connection string",
    )
    qdrant_url: Optional[str] = Field(
        default=os.getenv("QDRANT_URL"),
        description="Qdrant vector database endpoint",
    )
    jwt_secret: Optional[str] = Field(
        default=os.getenv("JWT_SECRET"),
        description="JWT secret used for protected endpoints",
    )

    # AI Provider API Keys
    openai_api_key: Optional[str] = Field(
        default=os.getenv("OPENAI_API_KEY"),
        description="API key for OpenAI",
    )
    anthropic_api_key: Optional[str] = Field(
        default=os.getenv("ANTHROPIC_API_KEY"),
        description="API key for Anthropic",
    )
    google_api_key: Optional[str] = Field(
        default=os.getenv(
            "GOOGLE_AI_API_KEY", os.getenv("GOOGLE_API_KEY")
        ),
        description="API key for Google AI",
    )
    mistral_api_key: Optional[str] = Field(
        default=os.getenv("MISTRAL_API_KEY"),
        description="API key for Mistral AI",
    )
    openrouter_api_key: Optional[str] = Field(
        default=os.getenv("OPENROUTER_API_KEY"),
        description="API key for OpenRouter",
    )
    deepseek_api_key: Optional[str] = Field(
        default=os.getenv("DEEPSEEK_API_KEY"),
        description="API key for DeepSeek",
    )


# Global settings instance
settings = Settings()

# Environment-specific overrides
if settings.environment == "production":
    settings.debug = False
    if settings.log_level == "INFO":  # respect explicit overrides
        settings.log_level = "WARNING"
elif settings.environment == "staging" and settings.log_level == "INFO":
    settings.debug = False
    settings.log_level = "INFO"

