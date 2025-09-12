#!/usr/bin/env python3
"""
Setup Build Environment for Chonost Desktop App
ติดตั้ง environment ที่จำเป็นสำหรับการ build desktop app
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
import urllib.request
import zipfile

class BuildEnvironmentSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.is_windows = platform.system() == "Windows"

    def run_command(self, command, cwd=None, description=""):
        """รันคำสั่งและจัดการ error"""
        print(f"🔧 {description}")
        print(f"📝 Command: {' '.join(command) if isinstance(command, list) else command}")

        try:
            if isinstance(command, str):
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    shell=True,
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    capture_output=True,
                    text=True
                )

            if result.returncode == 0:
                print("✅ Success")
                return result.stdout.strip(), result.stderr.strip()
            else:
                print(f"❌ Failed with code {result.returncode}")
                print(f"❌ Error: {result.stderr}")
                return None, result.stderr
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, str(e)

    def check_node_npm(self):
        """ตรวจสอบ Node.js และ npm"""
        print("📦 Checking Node.js and npm...")

        # Check Node.js
        stdout, stderr = self.run_command(["node", "--version"], description="Checking Node.js")
        if not stdout:
            print("❌ Node.js not found")
            return False
        print(f"✅ Node.js: {stdout}")

        # Check npm
        stdout, stderr = self.run_command(["npm", "--version"], description="Checking npm")
        if not stdout:
            print("❌ npm not found")
            return False
        print(f"✅ npm: {stdout}")

        return True

    def check_python(self):
        """ตรวจสอบ Python"""
        print("🐍 Checking Python...")

        stdout, stderr = self.run_command(["python", "--version"], description="Checking Python")
        if not stdout:
            stdout, stderr = self.run_command(["python3", "--version"], description="Checking Python3")

        if not stdout:
            print("❌ Python not found")
            return False

        print(f"✅ Python: {stdout}")
        return True

    def check_rust(self):
        """ตรวจสอบและติดตั้ง Rust"""
        print("🦀 Checking Rust/Cargo...")

        stdout, stderr = self.run_command(["cargo", "--version"], description="Checking Cargo")
        if stdout:
            print(f"✅ Rust: {stdout}")
            return True

        print("⚠️  Rust not found. Installing Rust...")

        # Download and install Rust
        try:
            if self.is_windows:
                rustup_url = "https://win.rustup.rs/x86_64"
                installer_path = self.project_root / "rustup-init.exe"

                print("📥 Downloading Rust installer...")
                urllib.request.urlretrieve(rustup_url, installer_path)

                print("⚙️ Installing Rust...")
                result = subprocess.run(
                    [str(installer_path), "-y", "--default-toolchain", "stable"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print("✅ Rust installed successfully")
                    # Clean up
                    installer_path.unlink(missing_ok=True)
                    return True
                else:
                    print(f"❌ Failed to install Rust: {result.stderr}")
                    return False
            else:
                # For Linux/Mac
                rustup_script = """
                curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
                """
                print("📥 Installing Rust via rustup...")
                result = subprocess.run(
                    rustup_script,
                    shell=True,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print("✅ Rust installed successfully")
                    return True
                else:
                    print(f"❌ Failed to install Rust: {result.stderr}")
                    return False

        except Exception as e:
            print(f"❌ Error installing Rust: {e}")
            return False

    def install_frontend_dependencies(self):
        """ติดตั้ง frontend dependencies"""
        print("🌐 Installing frontend dependencies...")

        frontend_dirs = [
            self.project_root / "packages" / "frontend",
            self.project_root / "craft-ide",
            self.project_root / "packages" / "ui"
        ]

        for frontend_dir in frontend_dirs:
            if frontend_dir.exists():
                print(f"📁 Installing in {frontend_dir.name}...")

                # Create .npmrc to avoid workspace issues
                npmrc_path = frontend_dir / ".npmrc"
                with open(npmrc_path, "w") as f:
                    f.write("ignore-workspace=true\nworkspace-concurrency=1\n")

                # Install dependencies
                stdout, stderr = self.run_command(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    description=f"Installing {frontend_dir.name} dependencies"
                )

                if not stdout and not stderr:
                    print(f"❌ Failed to install dependencies in {frontend_dir.name}")
                    return False

        return True

    def check_tauri_cli(self):
        """ตรวจสอบและติดตั้ง Tauri CLI"""
        print("⚙️ Checking Tauri CLI...")

        stdout, stderr = self.run_command(["npm", "list", "-g", "@tauri-apps/cli"], description="Checking Tauri CLI")
        if stdout and "@tauri-apps/cli" in stdout:
            print("✅ Tauri CLI found")
            return True

        print("⚠️  Tauri CLI not found. Installing...")

        stdout, stderr = self.run_command(
            ["npm", "install", "-g", "@tauri-apps/cli"],
            description="Installing Tauri CLI"
        )

        if not stdout:
            print("❌ Failed to install Tauri CLI")
            return False

        print("✅ Tauri CLI installed")
        return True

    def verify_setup(self):
        """ตรวจสอบการตั้งค่าทั้งหมด"""
        print("🔍 Verifying setup...")

        checks = [
            ("Node.js & npm", self.check_node_npm),
            ("Python", self.check_python),
            ("Rust/Cargo", self.check_rust),
            ("Tauri CLI", self.check_tauri_cli)
        ]

        all_passed = True
        for check_name, check_function in checks:
            print(f"\n📋 Checking {check_name}:")
            if not check_function():
                all_passed = False
                print(f"❌ {check_name} check failed")

        return all_passed

    def create_build_script(self):
        """สร้าง build script ที่พร้อมใช้งาน"""
        print("📝 Creating build script...")

        build_script = f"""#!/bin/bash
# Chonost Desktop App Build Script
# Generated by setup_build_environment.py

echo "🚀 Building Chonost Desktop App"
echo "==============================="

# Set project root
PROJECT_ROOT="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$PROJECT_ROOT"

# Frontend build
echo "🏗️ Building frontend..."
cd packages/frontend
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

# Desktop app build
echo "💻 Building desktop app..."
npm run tauri build
if [ $? -ne 0 ]; then
    echo "❌ Desktop app build failed"
    exit 1
fi

echo "✅ Build completed!"
echo "📁 Check packages/frontend/src-tauri/target/release/ for executable"
"""

        script_path = self.project_root / "build_app.sh"
        with open(script_path, "w", newline='\n') as f:
            f.write(build_script)

        # Make executable on Unix systems
        if not self.is_windows:
            os.chmod(script_path, 0o755)

        print(f"✅ Build script created: {script_path}")

        return True

    def run_full_setup(self):
        """รันการตั้งค่าทั้งหมด"""
        print("🚀 Chonost Desktop App Environment Setup")
        print("=" * 50)

        steps = [
            ("Verify current setup", self.verify_setup),
            ("Install frontend dependencies", self.install_frontend_dependencies),
            ("Create build script", self.create_build_script)
        ]

        for step_name, step_function in steps:
            print(f"\n🔄 {step_name}...")
            print("-" * 40)

            if not step_function():
                print(f"❌ {step_name} failed")
                return False
            else:
                print(f"✅ {step_name} completed")

        print("\n" + "=" * 50)
        print("🎉 Environment setup completed!")
        print("=" * 50)
        print("📋 Next steps:")
        print("1. Run build script: python build_desktop_simple.py")
        print("2. Or use batch script: build_desktop.bat (Windows)")
        print("3. Check output in packages/frontend/src-tauri/target/release/")

        return True

def main():
    setup = BuildEnvironmentSetup()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            setup.verify_setup()
        elif command == "deps":
            setup.install_frontend_dependencies()
        elif command == "rust":
            setup.check_rust()
        elif command == "tauri":
            setup.check_tauri_cli()
        else:
            print("Usage: python setup_build_environment.py [check|deps|rust|tauri]")
            print("  check  - Verify current setup")
            print("  deps   - Install frontend dependencies")
            print("  rust   - Check/install Rust")
            print("  tauri  - Check/install Tauri CLI")
    else:
        # Run full setup by default
        success = setup.run_full_setup()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
