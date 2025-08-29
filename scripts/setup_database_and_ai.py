#!/usr/bin/env python3
"""
Setup Database and AI Integration Script
ติดตั้งฐานข้อมูลและ AI integration สำหรับ Chonost
"""

import os
import sys
import subprocess
import asyncio
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

def setup_sqlite_database():
    """Setup SQLite database (faster than PostgreSQL)"""
    print("\n🗄️ Setting up SQLite Database...")
    
    backend_dir = Path("packages/backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install backend dependencies
    print("📦 Installing backend dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Install SQLite dependencies
    print("📦 Installing SQLite dependencies...")
    if not run_command("pip install aiosqlite", cwd=backend_dir):
        return False
    
    # Create database directory
    db_dir = backend_dir / "data"
    db_dir.mkdir(exist_ok=True)
    
    print("✅ SQLite database setup completed")
    return True

def setup_ai_integration():
    """Setup AI integration services"""
    print("\n🤖 Setting up AI Integration...")
    
    # Create AI service files
    ai_dir = Path("packages/backend/src/services")
    ai_dir.mkdir(parents=True, exist_ok=True)
    
    # AI Router Service
    ai_router_content = '''#!/usr/bin/env python3
"""
AI Router Service for Chonost
Routes requests to appropriate AI providers
"""

import asyncio
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
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=request.get("model", "gpt-4"),
                messages=request.get("messages", []),
                max_tokens=request.get("max_tokens", 1000),
                temperature=request.get("temperature", 0.7)
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "provider": "openai",
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }
    
    async def _handle_anthropic_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Anthropic request"""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=request.get("model", "claude-3-sonnet-20240229"),
                max_tokens=request.get("max_tokens", 1000),
                messages=request.get("messages", [])
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "provider": "anthropic",
                "model": response.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "anthropic"
            }

# Global AI router instance
ai_router = AIRouter()
'''
    
    with open(ai_dir / "ai_router.py", 'w') as f:
        f.write(ai_router_content)
    
    # AI API Routes
    ai_routes_content = '''#!/usr/bin/env python3
"""
AI API Routes for Chonost
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.ai_router import ai_router

router = APIRouter()

class AIRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4"
    messages: List[Dict[str, str]]
    max_tokens: int = 1000
    temperature: float = 0.7

class AIResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    provider: str
    model: Optional[str] = None

@router.post("/chat", response_model=AIResponse)
async def chat_with_ai(request: AIRequest):
    """Chat with AI provider"""
    try:
        result = await ai_router.route_request(request.dict())
        return AIResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_available_providers():
    """Get available AI providers"""
    providers = []
    
    if ai_router.openai_client:
        providers.append("openai")
    
    if ai_router.anthropic_client:
        providers.append("anthropic")
    
    return {"providers": providers}
'''
    
    with open(ai_dir / "ai_routes.py", 'w') as f:
        f.write(ai_routes_content)
    
    return True

def setup_local_ai_models():
    """Setup local AI models"""
    print("\n🤖 Setting up Local AI Models...")
    
    # Create models directory
    models_dir = Path("packages/backend/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Install local AI dependencies
    backend_dir = Path("packages/backend")
    print("📦 Installing local AI dependencies...")
    
    local_ai_deps = [
        "transformers",
        "torch",
        "sentence-transformers",
        "ctransformers",
        "llama-cpp-python"
    ]
    
    for dep in local_ai_deps:
        if not run_command(f"pip install {dep}", cwd=backend_dir):
            print(f"⚠️ Warning: Failed to install {dep}")
    
    # Create local AI service
    local_ai_content = '''#!/usr/bin/env python3
"""
Local AI Models Service for Chonost
"""

import os
from typing import Dict, Any, List
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import torch

class LocalAIService:
    """Local AI models service"""
    
    def __init__(self):
        self.models_dir = Path("./models")
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models = {}
        self.embedding_model = None
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        """Load sentence embedding model"""
        try:
            model_name = "all-MiniLM-L6-v2"
            self.embedding_model = SentenceTransformer(model_name)
            print(f"✅ Loaded embedding model: {model_name}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to load embedding model: {e}")
    
    async def generate_text(self, prompt: str, model_name: str = "local") -> Dict[str, Any]:
        """Generate text using local model"""
        try:
            # Simple text generation (placeholder)
            response = f"Local AI response to: {prompt[:50]}..."
            return {
                "success": True,
                "content": response,
                "provider": "local",
                "model": model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "local"
            }
    
    async def get_embeddings(self, text: str) -> List[float]:
        """Get text embeddings"""
        if self.embedding_model:
            try:
                embeddings = self.embedding_model.encode(text)
                return embeddings.tolist()
            except Exception as e:
                print(f"Error getting embeddings: {e}")
                return []
        return []

# Global local AI service instance
local_ai_service = LocalAIService()
'''
    
    services_dir = Path("packages/backend/src/services")
    with open(services_dir / "local_ai.py", 'w') as f:
        f.write(local_ai_content)
    
    return True

def setup_file_system():
    """Setup file upload and processing system"""
    print("\n📁 Setting up File System...")
    
    # Create upload directories
    upload_dir = Path("packages/backend/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create file processing service
    file_service_content = '''#!/usr/bin/env python3
"""
File Processing Service for Chonost
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from core.config import settings

class FileService:
    """File upload and processing service"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Save uploaded file"""
        try:
            # Create user directory
            user_dir = self.upload_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            file_path = user_dir / f"{file.filename}"
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            return {
                "success": True,
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "mime_type": file.content_type
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_user_files(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's uploaded files"""
        try:
            user_dir = self.upload_dir / user_id
            if not user_dir.exists():
                return []
            
            files = []
            for file_path in user_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        "filename": file_path.name,
                        "file_path": str(file_path),
                        "file_size": file_path.stat().st_size,
                        "created_at": file_path.stat().st_ctime
                    })
            
            return files
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Global file service instance
file_service = FileService()
'''
    
    services_dir = Path("packages/backend/src/services")
    with open(services_dir / "file_service.py", 'w') as f:
        f.write(file_service_content)
    
    return True

def setup_authentication():
    """Setup user authentication system"""
    print("\n🔐 Setting up Authentication...")
    
    # Create authentication service
    auth_service_content = '''#!/usr/bin/env python3
"""
Authentication Service for Chonost
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from core.database import get_db
from models.user import User

security = HTTPBearer()

class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def authenticate_user(self, username: str, password: str, db: AsyncSession) -> Optional[User]:
        """Authenticate user with username and password"""
        # Implementation here
        pass
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)) -> User:
        """Get current authenticated user"""
        token = credentials.credentials
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        # Implementation here
        pass

# Global auth service instance
auth_service = AuthService()
'''
    
    services_dir = Path("packages/backend/src/services")
    with open(services_dir / "auth_service.py", 'w') as f:
        f.write(auth_service_content)
    
    return True

def update_main_routes():
    """Update main routes to include new services"""
    print("\n🔗 Updating API Routes...")
    
    # Update main routes
    routes_content = '''#!/usr/bin/env python3
"""
Main API routes for Chonost
"""

from fastapi import APIRouter
from api.mongodb_routes import router as mongodb_router
from api.ai_routes import router as ai_router

router = APIRouter()

# Include other routers
router.include_router(mongodb_router, prefix="/mongodb", tags=["mongodb"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Chonost API", "version": "1.0.0"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chonost-api"}
'''
    
    routes_file = Path("packages/backend/src/api/routes.py")
    with open(routes_file, 'w') as f:
        f.write(routes_content)
    
    return True

def main():
    """Main setup function"""
    print("🚀 Chonost Database & AI Setup (SQLite Version)")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Setup steps
    steps = [
        ("SQLite Database", setup_sqlite_database),
        ("AI Integration", setup_ai_integration),
        ("Local AI Models", setup_local_ai_models),
        ("File System", setup_file_system),
        ("Authentication", setup_authentication),
        ("API Routes", update_main_routes),
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
    print("3. The Tauri frontend should already be running")
    
    return True

if __name__ == "__main__":
    main()
