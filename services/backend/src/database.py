"""
Database utilities and connection management

This module provides centralized database connection management
and utilities for the Chat Integration Backend.
"""

import os
import sqlite3
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator


async def get_db_connection() -> sqlite3.Connection:
    """Get database connection.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    database_path = os.environ.get('DATABASE_PATH', 'chonost.db')

    # Ensure database directory exists
    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


async def close_db_connection(conn: sqlite3.Connection):
    """Close database connection.

    Args:
        conn: Database connection object.
    """
    if conn is not None:
        conn.close()


@asynccontextmanager
async def get_db_transaction() -> AsyncGenerator[sqlite3.Connection, None]:
    """Async context manager for database transactions.

    Yields:
        sqlite3.Connection: Database connection object.
    """
    conn = await get_db_connection()
    try:
        yield conn
        await asyncio.get_event_loop().run_in_executor(None, conn.commit)
    except Exception:
        await asyncio.get_event_loop().run_in_executor(None, conn.rollback)
        raise
    finally:
        await asyncio.get_event_loop().run_in_executor(None, conn.close)


async def init_db():
    """Initialize database with schema."""
    conn = await get_db_connection()

    # Create tables if they don't exist
    await asyncio.get_event_loop().run_in_executor(None, conn.executescript, '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        );
        
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            upload_type TEXT DEFAULT 'general',
            processed_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            config TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS workflow_executions (
            id TEXT PRIMARY KEY,
            workflow_id TEXT NOT NULL,
            status TEXT NOT NULL,
            input_data TEXT,
            output_data TEXT,
            error_message TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows (id)
        );
        
        CREATE TABLE IF NOT EXISTS service_connections (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            connection_config TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
        CREATE TABLE IF NOT EXISTS automation_templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            template_config TEXT NOT NULL,
            is_public BOOLEAN DEFAULT FALSE,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        );
    ''')

    await asyncio.get_event_loop().run_in_executor(None, conn.commit)
    await asyncio.get_event_loop().run_in_executor(None, conn.close)


async def init_app(app):
    """Initialize database with FastAPI app.

    Args:
        app: FastAPI application instance.
    """
    # Initialize database on startup
    await init_db()


# Migration utilities (for future PostgreSQL migration)
def get_migration_scripts():
    """Get list of migration scripts.
    
    Returns:
        list: List of migration script paths.
    """
    migration_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    if not os.path.exists(migration_dir):
        return []
    
    scripts = []
    for filename in sorted(os.listdir(migration_dir)):
        if filename.endswith('.sql'):
            scripts.append(os.path.join(migration_dir, filename))
    
    return scripts


def run_migrations():
    """Run pending database migrations.
    
    This function will be used when migrating to PostgreSQL.
    """
    # This will be implemented when migrating to PostgreSQL
    pass


# PostgreSQL utilities (for future migration)
def get_postgresql_connection_string():
    """Get PostgreSQL connection string from environment.
    
    Returns:
        str: PostgreSQL connection string.
    """
    return os.environ.get(
        'POSTGRESQL_URL',
        'postgresql://localhost:5432/chat_integration'
    )


def migrate_to_postgresql():
    """Migrate data from SQLite to PostgreSQL.
    
    This function will handle the migration process when moving to PostgreSQL.
    """
    # This will be implemented when migrating to PostgreSQL
    pass

