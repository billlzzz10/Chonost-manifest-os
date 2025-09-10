#!/usr/bin/env python3
"""
Setup script for MCP AI Orchestrator
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

def run_command(cmd: str, cwd: Optional[str] = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            check=True
        )
        print(f"✅ {cmd}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies() -> bool:
    """Install project dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Install main package in development mode
    if not run_command("pip install -e ."):
        return False
    
    # Install optional dependencies
    optional_deps = ["agent", "dataset", "dev"]
    for dep in optional_deps:
        if not run_command(f"pip install -e '.[{dep}]'"):
            print(f"⚠️ Warning: Failed to install {dep} dependencies")
    
    return True

def setup_mcp_server() -> bool:
    """Setup the MCP Server."""
    print("\n🔧 Setting up MCP Server...")
    
    mcp_server_dir = Path("services/mcp-server")
    if not mcp_server_dir.exists():
        print("❌ MCP Server directory not found")
        return False
    
    # Install MCP Server dependencies
    if not run_command("pip install -r requirements.txt", str(mcp_server_dir)):
        return False
    
    print("✅ MCP Server setup complete")
    return True

def create_directories() -> bool:
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "logs", 
        "docs",
        "tests",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")
    
    return True

def setup_environment() -> bool:
    """Setup environment variables."""
    print("\n🔐 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from template")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️ No .env template found")
    
    return True

def main() -> None:
    """Main setup function."""
    print("🚀 Setting up MCP AI Orchestrator...")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup MCP Server
    if not setup_mcp_server():
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\n📖 Next steps:")
    print("1. Configure your .env file")
    print("2. Run the MCP Server: python -m src.mcp_ai_orchestrator.main")
    print("3. Or use the CLI: mcp-cli")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
