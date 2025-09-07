#!/usr/bin/env python3
"""
Chonost Desktop App Build System
ระบบสร้างแอปเดสก์ท็อปแบบครบถ้วน
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

class DesktopAppBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_info = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0",
            "platform": sys.platform,
            "tests_passed": False,
            "build_success": False,
            "artifacts": []
        }

    def run_command(self, command, cwd=None, description=""):
        """รันคำสั่งและจัดการ error"""
        print(f"🔧 {description}")
        print(f"📝 Command: {' '.join(command)}")
        print(f"📁 Working directory: {cwd or self.project_root}")

        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Success")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed with exit code {e.returncode}")
            print(f"❌ Error output: {e.stderr}")
            return None

    def check_system_requirements(self):
        """ตรวจสอบระบบที่จำเป็น"""
        print("🔍 Checking system requirements...")

        # Check Node.js
        node_result = self.run_command(["node", "--version"], description="Checking Node.js")
        if not node_result:
            print("❌ Node.js not found. Please install Node.js >= 18.0.0")
            return False

        # Check npm
        npm_result = self.run_command(["npm", "--version"], description="Checking npm")
        if not npm_result:
            print("❌ npm not found. Please install npm")
            return False

        # Check Python
        python_result = self.run_command(["python", "--version"], description="Checking Python")
        if not python_result:
            python_result = self.run_command(["python3", "--version"], description="Checking Python3")

        if not python_result:
            print("❌ Python not found. Please install Python >= 3.8")
            return False

        # Check Rust (for Tauri)
        rust_result = self.run_command(["cargo", "--version"], description="Checking Rust/Cargo")
        if not rust_result:
            print("⚠️  Rust/Cargo not found. Installing Rust...")
            self.install_rust()

        print("✅ System requirements check passed")
        return True

    def install_rust(self):
        """ติดตั้ง Rust"""
        try:
            import urllib.request

            print("📥 Downloading Rust installer...")
            rustup_url = "https://sh.rustup.rs"
            rustup_script = urllib.request.urlopen(rustup_url).read().decode('utf-8')

            # Save to temp file
            with open("rustup-init.sh", "w") as f:
                f.write(rustup_script)

            # Run installer
            result = self.run_command(
                ["sh", "rustup-init.sh", "-y"],
                description="Installing Rust"
            )

            if result:
                # Clean up
                os.remove("rustup-init.sh")
                print("✅ Rust installed successfully")
                return True
            else:
                print("❌ Failed to install Rust")
                return False

        except Exception as e:
            print(f"❌ Error installing Rust: {e}")
            return False

    def install_dependencies(self):
        """ติดตั้ง dependencies"""
        print("📦 Installing dependencies...")

        # Install frontend dependencies
        frontend_dir = self.project_root / "packages" / "frontend"
        if frontend_dir.exists():
            print("🌐 Installing frontend dependencies...")
            result = self.run_command(
                ["npm", "install"],
                cwd=frontend_dir,
                description="Installing frontend dependencies"
            )
            if not result:
                return False

        # Install craft-ide dependencies
        craft_dir = self.project_root / "craft-ide"
        if craft_dir.exists():
            print("🛠️ Installing Craft IDE dependencies...")
            result = self.run_command(
                ["npm", "install"],
                cwd=craft_dir,
                description="Installing Craft IDE dependencies"
            )
            if not result:
                return False

        # Install UI package dependencies
        ui_dir = self.project_root / "packages" / "ui"
        if ui_dir.exists():
            print("🎨 Installing UI package dependencies...")
            result = self.run_command(
                ["npm", "install"],
                cwd=ui_dir,
                description="Installing UI package dependencies"
            )
            if not result:
                return False

        print("✅ All dependencies installed")
        return True

    def run_comprehensive_tests(self):
        """รันการทดสอบครบถ้วน"""
        print("🧪 Running comprehensive tests...")

        # Start backend server for testing
        print("🔧 Starting backend server for testing...")
        backend_process = self.start_backend_server()

        if backend_process:
            time.sleep(3)  # Wait for server to start

            # Run comprehensive tests
            result = self.run_command(
                [sys.executable, "comprehensive_testing.py"],
                description="Running comprehensive tests"
            )

            # Stop backend server
            backend_process.terminate()
            backend_process.wait()

            if result:
                self.build_info["tests_passed"] = True
                print("✅ All tests passed")
                return True
            else:
                print("❌ Tests failed")
                return False
        else:
            print("❌ Could not start backend server for testing")
            return False

    def start_backend_server(self):
        """เริ่ม backend server"""
        try:
            backend_dir = self.project_root / "services" / "local-rag"
            if backend_dir.exists():
                return subprocess.Popen(
                    [sys.executable, "simple_server.py"],
                    cwd=backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                print("❌ Backend directory not found")
                return None
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return None

    def build_frontend_app(self):
        """สร้าง frontend app ด้วย Tauri"""
        print("🏗️ Building frontend desktop app...")

        frontend_dir = self.project_root / "packages" / "frontend"

        # Build web assets
        result = self.run_command(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            description="Building frontend assets"
        )
        if not result:
            return False

        # Build desktop app with Tauri
        result = self.run_command(
            ["npm", "run", "tauri", "build"],
            cwd=frontend_dir,
            description="Building desktop app with Tauri"
        )
        if not result:
            return False

        # Find the built executable
        target_dir = frontend_dir / "src-tauri" / "target" / "release"
        if target_dir.exists():
            exe_files = list(target_dir.glob("*.exe"))
            if exe_files:
                exe_path = exe_files[0]
                self.build_info["artifacts"].append({
                    "type": "executable",
                    "path": str(exe_path),
                    "name": exe_path.name,
                    "size": exe_path.stat().st_size
                })
                print(f"✅ Desktop app built: {exe_path}")
                return True

        print("❌ Could not find built executable")
        return False

    def build_craft_ide_app(self):
        """สร้าง Craft IDE app ด้วย Tauri"""
        print("🛠️ Building Craft IDE desktop app...")

        craft_dir = self.project_root / "craft-ide"

        # Build web assets
        result = self.run_command(
            ["npm", "run", "build"],
            cwd=craft_dir,
            description="Building Craft IDE assets"
        )
        if not result:
            return False

        # Build desktop app with Tauri
        result = self.run_command(
            ["npm", "run", "tauri", "build"],
            cwd=craft_dir,
            description="Building Craft IDE desktop app with Tauri"
        )
        if not result:
            return False

        # Find the built executable
        target_dir = craft_dir / "src-tauri" / "target" / "release"
        if target_dir.exists():
            exe_files = list(target_dir.glob("*.exe"))
            if exe_files:
                exe_path = exe_files[0]
                self.build_info["artifacts"].append({
                    "type": "craft-ide-executable",
                    "path": str(exe_path),
                    "name": exe_path.name,
                    "size": exe_path.stat().st_size
                })
                print(f"✅ Craft IDE app built: {exe_path}")
                return True

        print("❌ Could not find Craft IDE executable")
        return False

    def create_installer(self):
        """สร้าง installer package"""
        print("📦 Creating installer package...")

        try:
            # Create dist directory
            dist_dir = self.project_root / "dist"
            dist_dir.mkdir(exist_ok=True)

            # Copy executables to dist
            for artifact in self.build_info["artifacts"]:
                if artifact["type"] == "executable":
                    source_path = Path(artifact["path"])
                    dest_path = dist_dir / source_path.name

                    import shutil
                    shutil.copy2(source_path, dest_path)
                    print(f"✅ Copied {source_path.name} to dist/")

            # Create version info
            version_file = dist_dir / "version.json"
            with open(version_file, "w", encoding="utf-8") as f:
                json.dump({
                    "version": self.build_info["version"],
                    "build_time": self.build_info["timestamp"],
                    "platform": self.build_info["platform"],
                    "artifacts": self.build_info["artifacts"]
                }, f, indent=2)

            print(f"✅ Installer package created in {dist_dir}")
            return True

        except Exception as e:
            print(f"❌ Error creating installer: {e}")
            return False

    def save_build_info(self):
        """บันทึกข้อมูลการ build"""
        build_info_file = self.project_root / "build_info.json"

        with open(build_info_file, "w", encoding="utf-8") as f:
            json.dump(self.build_info, f, indent=2)

        print(f"✅ Build info saved to {build_info_file}")

    def run_full_build(self):
        """รันการ build แบบครบถ้วน"""
        print("🚀 Starting Chonost Desktop App Build Process")
        print("=" * 60)

        start_time = time.time()

        try:
            # 1. Check system requirements
            if not self.check_system_requirements():
                print("❌ System requirements check failed")
                return False

            # 2. Install dependencies
            if not self.install_dependencies():
                print("❌ Dependencies installation failed")
                return False

            # 3. Run comprehensive tests
            if not self.run_comprehensive_tests():
                print("❌ Comprehensive tests failed")
                return False

            # 4. Build frontend desktop app
            if not self.build_frontend_app():
                print("❌ Frontend desktop app build failed")
                return False

            # 5. Build Craft IDE desktop app
            if not self.build_craft_ide_app():
                print("❌ Craft IDE desktop app build failed")
                return False

            # 6. Create installer package
            if not self.create_installer():
                print("❌ Installer creation failed")
                return False

            # Mark build as successful
            self.build_info["build_success"] = True

            # Save build info
            self.save_build_info()

            build_time = time.time() - start_time

            print("\n" + "=" * 60)
            print("🎉 BUILD SUCCESSFUL!")
            print("=" * 60)
            print("📦 Built artifacts:")
            for artifact in self.build_info["artifacts"]:
                print(f"   • {artifact['name']} ({artifact['size'] / (1024*1024):.1f} MB)")

            print(f"\n⏱️  Total build time: {build_time:.1f} seconds")
            print("📁 Output directory: dist/")
            print("\n🚀 Ready to distribute!")

            return True

        except Exception as e:
            print(f"❌ Build failed with error: {e}")
            return False

def main():
    builder = DesktopAppBuilder()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            builder.run_comprehensive_tests()
        elif command == "build":
            builder.run_full_build()
        elif command == "deps":
            builder.install_dependencies()
        elif command == "check":
            builder.check_system_requirements()
        else:
            print("Usage: python build_desktop_app.py [test|build|deps|check]")
            print("  test  - Run comprehensive tests")
            print("  build - Run full build process")
            print("  deps  - Install dependencies")
            print("  check - Check system requirements")
    else:
        # Run full build by default
        success = builder.run_full_build()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
