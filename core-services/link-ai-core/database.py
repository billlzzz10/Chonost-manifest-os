"""
Database connection and session management for the application.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

from config import settings

# Create an asynchronous engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo_log,
    future=True
)

# Create a session maker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_db_and_tables():
    """
    Creates all database tables defined by the Base metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)