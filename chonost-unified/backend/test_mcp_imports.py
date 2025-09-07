#!/usr/bin/env python3
"""
Test MCP imports to debug issues
"""

import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("Python path:")
for path in sys.path[:3]:
    print(f"  {path}")

print("\nTesting MCP imports...")

try:
    print("1. Testing models import...")
    from backend.mcp.models import MCPServer
    print("   ✓ models import successful")

    print("2. Testing registry import...")
    from backend.mcp.mcp.registry import MCPRegistry
    print("   ✓ registry import successful")

    print("3. Testing client import...")
    from backend.mcp.mcp.client import MCPClient
    print("   ✓ client import successful")

    print("4. Testing config import...")
    from backend.mcp.config import Settings
    print("   ✓ config import successful")

    print("5. Testing main MCP app import...")
    from backend.mcp.main import app as mcp_app
    print("   ✓ MCP app import successful")

    print("\n✅ All MCP imports successful!")

    # Test initialization
    print("\n6. Testing MCP component initialization...")
    settings = Settings()
    print(f"   ✓ Settings initialized: {settings.dict()}")

    mcp_registry = MCPRegistry()
    print("   ✓ MCP Registry initialized")

    mcp_client = MCPClient()
    print("   ✓ MCP Client initialized")

    print("\n🎉 MCP orchestrator ready!")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
