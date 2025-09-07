#!/usr/bin/env python3
"""
Simple Desktop App Build Script
สคริปต์สร้างแอปเดสก์ท็อปแบบง่าย
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """รันคำสั่งและแสดงผล"""
    print(f"🔧 {description}")
    print(f"📝 Command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print("✅ Success")
            return True
        else:
            print(f"❌ Failed with code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    project_root = Path(__file__).parent

    print("🚀 Chonost Desktop App Build")
    print("=" * 50)

    # 1. Check if we're in the right directory
    if not (project_root / "packages" / "frontend").exists():
        print("❌ Error: packages/frontend directory not found")
        print(f"Current directory: {project_root}")
        return False

    # 2. Install frontend dependencies
    frontend_dir = project_root / "packages" / "frontend"
    print(f"📦 Installing frontend dependencies in {frontend_dir}")
    if not run_command("npm install", cwd=frontend_dir, description="Installing frontend dependencies"):
        return False

    # 3. Build frontend
    print("🏗️ Building frontend...")
    if not run_command("npm run build", cwd=frontend_dir, description="Building frontend"):
        return False

    # 4. Build desktop app with Tauri
    print("💻 Building desktop app with Tauri...")
    if not run_command("npm run tauri build", cwd=frontend_dir, description="Building desktop app"):
        return False

    # 5. Check for built executable
    target_dir = frontend_dir / "src-tauri" / "target" / "release"
    if target_dir.exists():
        exe_files = list(target_dir.glob("*.exe"))
        if exe_files:
            exe_path = exe_files[0]
            print(f"\n🎉 SUCCESS! Desktop app built:")
            print(f"📁 Location: {exe_path}")
            print(f"📊 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            print("\n🚀 Ready to run!")
            return True

    print("❌ Could not find built executable")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
