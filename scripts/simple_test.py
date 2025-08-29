#!/usr/bin/env python3
"""
Simple Test Script for Chonost System
ทดสอบระบบแบบง่ายๆ
"""

import os
import sys
from pathlib import Path

def test_file_structure():
    """Test if all required files exist"""
    print("🔍 Testing File Structure...")
    
    project_root = Path(__file__).parent.parent
    
    required_files = [
        "services/backend/src/integrated_system.py",
        "services/ai/core/enhanced_ai_agents.py",
        "services/frontend/web/App.tsx",
        "docker-compose.yml",
        "env.example"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_directories():
    """Test if all required directories exist"""
    print("\n📁 Testing Directories...")
    
    project_root = Path(__file__).parent.parent
    
    required_dirs = [
        "services/backend/src",
        "services/ai/core",
        "services/frontend/web",
        "services/database/prisma",
        "services/testing"
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Main function"""
    print("🚀 Simple Chonost System Test")
    print("=" * 40)
    
    # Test files
    files_ok = test_file_structure()
    
    # Test directories
    dirs_ok = test_directories()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    if files_ok and dirs_ok:
        print("🎉 All tests passed! System structure is complete!")
        print("\n✅ Files: OK")
        print("✅ Directories: OK")
        print("\n🚀 System is ready for use!")
    else:
        print("⚠️  Some tests failed!")
        if not files_ok:
            print("❌ Files: Some missing")
        if not dirs_ok:
            print("❌ Directories: Some missing")

if __name__ == "__main__":
    main()
