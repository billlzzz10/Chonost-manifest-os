"""
Orchestrator Configuration Override
สามารถ override ค่า config ได้ตามต้องการ
"""

import os
from typing import Dict, Any

# Environment-specific overrides
ENVIRONMENT_OVERRIDES = {
    "development": {
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "true",
        "MCP_POOL_MAX": "2",
        "MCP_TTL_SECONDS": "60"
    },
    "staging": {
        "LOG_LEVEL": "INFO",
        "DEBUG": "false",
        "MCP_POOL_MAX": "4",
        "MCP_TTL_SECONDS": "300"
    },
    "production": {
        "LOG_LEVEL": "WARNING",
        "DEBUG": "false",
        "MCP_POOL_MAX": "8",
        "MCP_TTL_SECONDS": "600"
    }
}

def apply_environment_overrides():
    """Apply environment-specific configuration overrides"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env in ENVIRONMENT_OVERRIDES:
        overrides = ENVIRONMENT_OVERRIDES[env]
        for key, value in overrides.items():
            if key not in os.environ:
                os.environ[key] = value
                print(f"🔧 Applied {env} override: {key}={value}")

def get_custom_server_configs() -> Dict[str, Any]:
    """Get custom MCP server configurations"""
    return {
        # สามารถเพิ่ม custom server configs ได้ที่นี่
        "custom_filesystem": {
            "name": "custom_filesystem",
            "cmd": ["python", "custom_fs_server.py"],
            "description": "Custom File System Server",
            "version": "1.0.0",
            "env": {
                "CUSTOM_MODE": "enabled",
                "DEBUG": "true"
            }
        }
    }

def setup_development_environment():
    """Setup development environment"""
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("HOST", "127.0.0.1")
    os.environ.setdefault("PORT", "8000")
    
    print("🔧 Development environment configured")

def setup_production_environment():
    """Setup production environment"""
    os.environ.setdefault("ENVIRONMENT", "production")
    os.environ.setdefault("LOG_LEVEL", "WARNING")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    
    print("🔧 Production environment configured")

# Auto-apply overrides when module is imported
if __name__ != "__main__":
    apply_environment_overrides()
