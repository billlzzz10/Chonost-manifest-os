#!/usr/bin/env python3
"""
Configuration settings for Chonost FastAPI Backend
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Chonost API"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:1420"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database - Use SQLite for faster setup
    DATABASE_URL: str = Field(
        default="sqlite:///./chonost.db",
        env="DATABASE_URL"
    )
    
    # MongoDB
    MONGODB_URL: str = Field(
        default="mongodb+srv://billlzzz10_db_user:ZxFcv9L9EUPV27kM@cluster0.ep8seuu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        env="MONGODB_URL"
    )
    MONGODB_DATABASE: str = Field(
        default="chonost",
        env="MONGODB_DATABASE"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Vector Database (Qdrant)
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        env="QDRANT_URL"
    )
    QDRANT_COLLECTION: str = Field(
        default="chonost_embeddings",
        env="QDRANT_COLLECTION"
    )
    
    # AI Providers
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    AZURE_OPENAI_API_KEY: str = Field(default="", env="AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = Field(default="", env="AZURE_OPENAI_ENDPOINT")
    
    # Local AI Models
    LOCAL_AI_ENABLED: bool = Field(default=True, env="LOCAL_AI_ENABLED")
    LOCAL_MODEL_PATH: str = Field(default="./models", env="LOCAL_MODEL_PATH")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
