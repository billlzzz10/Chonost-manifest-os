#!/usr/bin/env python3
"""
Chonost Project Setup Script
ติดตั้ง dependencies และ setup ระบบทั้งหมด
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run command and return result"""
    print(f"🔄 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=shell, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            return True
        else:
            print(f"❌ Error: {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def setup_backend():
    """Setup FastAPI backend"""
    print("\n🚀 Setting up FastAPI Backend...")
    
    backend_dir = Path("packages/backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Create .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# Chonost Backend Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://chonost:chonost@localhost:5432/chonost

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=chonost_embeddings

# AI Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint

# Security
SECRET_KEY=your-secret-key-change-in-production
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    return True

def setup_frontend():
    """Setup Tauri frontend"""
    print("\n🎨 Setting up Tauri Frontend...")
    
    frontend_dir = Path("packages/frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    return True

def setup_database():
    """Setup PostgreSQL and Qdrant"""
    print("\n🗄️ Setting up Database...")
    
    # Check if Docker is available
    if not run_command("docker --version"):
        print("⚠️ Docker not found. Please install Docker first.")
        return False
    
    # Create docker-compose.yml for database services
    docker_compose_content = """version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: chonost_postgres
    environment:
      POSTGRES_DB: chonost
      POSTGRES_USER: chonost
      POSTGRES_PASSWORD: chonost
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: chonost_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: chonost_qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
"""
    
    with open("docker-compose.db.yml", 'w') as f:
        f.write(docker_compose_content)
    
    # Start database services
    print("🚀 Starting database services...")
    if not run_command("docker-compose -f docker-compose.db.yml up -d"):
        return False
    
    return True

def setup_ai_integration():
    """Setup AI integration"""
    print("\n🤖 Setting up AI Integration...")
    
    # Create AI service files
    ai_dir = Path("packages/backend/src/services")
    ai_dir.mkdir(parents=True, exist_ok=True)
    
    # AI Router
    ai_router_content = '''#!/usr/bin/env python3
"""
AI Router Service for Chonost
Routes requests to appropriate AI providers
"""

from typing import Dict, Any, Optional
import openai
import anthropic
from qdrant_client import QdrantClient
from core.config import settings

class AIRouter:
    """Routes AI requests to appropriate providers"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.qdrant_client = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup AI provider clients"""
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
        
        if settings.QDRANT_URL:
            self.qdrant_client = QdrantClient(settings.QDRANT_URL)
    
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route AI request to appropriate provider"""
        provider = request.get("provider", "openai")
        model = request.get("model", "gpt-4")
        
        if provider == "openai" and self.openai_client:
            return await self._handle_openai_request(request)
        elif provider == "anthropic" and self.anthropic_client:
            return await self._handle_anthropic_request(request)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _handle_openai_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OpenAI request"""
        # Implementation here
        pass
    
    async def _handle_anthropic_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Anthropic request"""
        # Implementation here
        pass
'''
    
    with open(ai_dir / "ai_router.py", 'w') as f:
        f.write(ai_router_content)
    
    return True

def setup_frontend_components():
    """Setup frontend components"""
    print("\n🎨 Setting up Frontend Components...")
    
    components_dir = Path("packages/frontend/src/components")
    components_dir.mkdir(parents=True, exist_ok=True)
    
    # Create basic component structure
    components = {
        "Layout": "Layout.tsx",
        "Editor": "Editor.tsx", 
        "Whiteboard": "Whiteboard.tsx",
        "KnowledgeExplorer": "KnowledgeExplorer.tsx",
        "AssistantPanel": "AssistantPanel.tsx",
        "RotaryTools": "RotaryTools.tsx"
    }
    
    for component_name, filename in components.items():
        component_dir = components_dir / component_name
        component_dir.mkdir(exist_ok=True)
        
        component_content = f'''import React from 'react';

interface {component_name}Props {{
  // Add props here
}}

export const {component_name}: React.FC<{component_name}Props> = () => {{
  return (
    <div className="{component_name.lower()}-container">
      <h2>{component_name}</h2>
      {{/* Component content */}}
    </div>
  );
}};

export default {component_name};
'''
        
        with open(component_dir / filename, 'w') as f:
            f.write(component_content)
    
    return True

def main():
    """Main setup function"""
    print("🚀 Chonost Project Setup")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Setup steps
    steps = [
        ("Backend Dependencies", setup_backend),
        ("Frontend Dependencies", setup_frontend),
        ("Database Setup", setup_database),
        ("AI Integration", setup_ai_integration),
        ("Frontend Components", setup_frontend_components),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"❌ Failed to setup {step_name}")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your AI API keys in packages/backend/.env")
    print("2. Start the backend: cd packages/backend && python src/main.py")
    print("3. Start the frontend: cd packages/frontend && npm run tauri:dev")
    
    return True

if __name__ == "__main__":
    main()
