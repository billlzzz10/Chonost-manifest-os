#!/usr/bin/env python3
"""
Legacy File Cleanup Script
"""

import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    project_root = Path(".")
    
    # Create directories
    directories = [
        "legacy",
        "deprecated", 
        "src/core",
        "src/api/routes",
        "src/services",
        "src/models",
        "src/utils",
        "src/config",
        "apps/web/public",
        "docs",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Move files to legacy
    legacy_moves = {
        "mobile_assistant_core.py": "src/core/conversation_service.py",
        "mobile_assistant_api.py": "src/api/routes/mobile.py",
        "enhanced_rag_system.py": "src/core/rag_system.py",
        "advanced_backend_agents.py": "src/core/ai_agents.py",
        "MOBILE_ASSISTANT_README.md": "docs/mobile-assistant.md",
    }
    
    for old_path, new_path in legacy_moves.items():
        if Path(old_path).exists():
            Path(new_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(old_path, new_path)
            logger.info(f"Moved {old_path} -> {new_path}")
    
    # Move deprecated files
    deprecated_files = [
        "manuscript_management.py",
        "app.py", 
        "test_manuscript_api.py",
        "requirements_manuscript.txt"
    ]
    
    for filename in deprecated_files:
        if Path(filename).exists():
            shutil.move(filename, f"deprecated/{filename}")
            logger.info(f"Moved deprecated: {filename}")
    
    logger.info("Cleanup completed!")

if __name__ == "__main__":
    main()
