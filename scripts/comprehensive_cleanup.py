#!/usr/bin/env python3
"""
Comprehensive Project Cleanup Script
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
        "legacy", "deprecated",
        "src/core", "src/api/routes", "src/services", "src/models", 
        "src/utils", "src/config", "src/middleware", "src/schemas",
        "apps/web/public", "apps/web/src", "apps/web/components",
        "apps/desktop/src", "apps/mobile/src",
        "docs/api", "docs/deployment", "docs/development",
        "tests/unit", "tests/integration", "tests/e2e", "tests/fixtures",
        "data/uploads", "data/exports", "logs",
        "scripts/deployment", "scripts/database", "scripts/ai"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Move files to new structure
    legacy_moves = {
        "enhanced_rag_system.py": "src/core/rag_system.py",
        "advanced_backend_agents.py": "src/core/ai_agents.py",
        "mobile_assistant_core.py": "src/core/conversation_service.py",
        "mobile_assistant_api.py": "src/api/routes/mobile.py",
        "mobile_assistant_integration.py": "src/core/mobile_integration.py",
        "dashboard_system.py": "src/services/analytics_service.py",
        "analytics_core.py": "src/services/analytics_core.py",
        "data_management.py": "src/services/data_service.py",
        "main_analytics_system.py": "src/services/analytics_main.py",
        "webhook_integration.py": "src/api/routes/webhook.py",
        "webhook_demo.py": "src/api/routes/webhook_demo.py",
        "advanced_mcp_agents.py": "src/core/mcp_agents.py",
        "real_mcp_integration.py": "src/core/mcp_integration.py",
        "demo_agents_system.py": "src/core/demo_agents.py",
        "self_learning_tools.py": "src/core/self_learning.py",
        "mobile_assistant_frontend.html": "apps/web/public/mobile-assistant.html",
        "MOBILE_ASSISTANT_README.md": "docs/mobile-assistant.md",
        "README_MANUSCRIPT.md": "docs/manuscript-system.md",
        "README_ENHANCED_RAG.md": "docs/rag-system.md",
        "README_WEBHOOK.md": "docs/webhook-integration.md",
        "README_ANALYTICS.md": "docs/analytics-system.md",
        "NOTION_API_SETUP.md": "docs/notion-integration.md",
        "AGENTS.md": "docs/agents.md",
        "DEMO_README.md": "docs/demo.md",
        "clickup_guide_summary.md": "docs/clickup-integration.md",
        "clickup_workflow_examples.md": "docs/clickup-workflows.md",
    }
    
    moved_count = 0
    for old_path, new_path in legacy_moves.items():
        if Path(old_path).exists():
            Path(new_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(old_path, new_path)
            logger.info(f"Moved {old_path} -> {new_path}")
            moved_count += 1
    
    # Move deprecated files
    deprecated_files = [
        "manuscript_management.py", "app.py", "test_manuscript_api.py",
        "requirements_manuscript.txt", "requirements_enhanced.txt",
        "requirements_analytics.txt", "requirements_webhook.txt",
        "requirements_notion.txt", "ultimate_demo.py",
        "clickup_processor_simple.py", "clickup_task_creation_guide.py",
        "notion_api_example.py", "enhanced_backend_agents.py",
        "advanced_rag_system.py"
    ]
    
    deprecated_count = 0
    for filename in deprecated_files:
        if Path(filename).exists():
            shutil.move(filename, f"deprecated/{filename}")
            logger.info(f"Moved deprecated: {filename}")
            deprecated_count += 1
    
    # Create __init__.py files
    init_dirs = [
        "src", "src/core", "src/api", "src/api/routes", "src/services",
        "src/models", "src/utils", "src/config", "src/middleware", "src/schemas",
        "tests", "tests/unit", "tests/integration", "tests/e2e"
    ]
    
    for directory in init_dirs:
        if Path(directory).exists():
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                logger.info(f"Created __init__.py in {directory}")
    
    logger.info(f"Cleanup completed! Moved {moved_count} files, deprecated {deprecated_count} files")

if __name__ == "__main__":
    main()
