#!/usr/bin/env python3
"""
Automated Testing and Deployment Script for Chonost Desktop App
ระบบทดสอบและการ deploy อัตโนมัติ
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

class AutomatedTester:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.deployment_info = {}

    def run_command(self, command, cwd=None, capture_output=True):
        """รันคำสั่งและจัดการ output"""
        try:
            # Check if command exists
            if command[0] in ['npm', 'node']:
                # Try to find the executable
                import shutil
                if not shutil.which(command[0]):
                    print(f"⚠️  {command[0]} not found in PATH")
                    return None, f"{command[0]} not found"

            if capture_output:
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip(), result.stderr.strip()
            else:
                result = subprocess.run(
                    command,
                    cwd=cwd or self.project_root,
                    check=True
                )
                return "", ""
        except FileNotFoundError:
            print(f"⚠️  Command not found: {' '.join(command)}")
            return None, f"Command not found: {command[0]}"
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"❌ Error: {e.stderr}")
            return None, e.stderr

    def test_frontend_linting(self):
        """ทดสอบ linting ของ frontend"""
        print("🔍 Testing Frontend Linting...")

        frontend_dirs = [
            self.project_root / "packages" / "frontend",
            self.project_root / "craft-ide",
            self.project_root / "packages" / "ui"
        ]

        lint_results = []
        for frontend_dir in frontend_dirs:
            if frontend_dir.exists():
                print(f"📁 Checking {frontend_dir.name}...")

                # Check if package.json has lint script
                package_json = frontend_dir / "package.json"
                if package_json.exists():
                    with open(package_json, "r") as f:
                        package_data = json.load(f)

                    if "scripts" in package_data and "lint" in package_data["scripts"]:
                        stdout, stderr = self.run_command(
                            ["npm", "run", "lint"],
                            cwd=frontend_dir
                        )
                        if stdout is not None:
                            lint_results.append({
                                "directory": str(frontend_dir),
                                "status": "PASS",
                                "output": stdout
                            })
                            print(f"✅ {frontend_dir.name}: PASS")
                        else:
                            lint_results.append({
                                "directory": str(frontend_dir),
                                "status": "FAIL",
                                "error": stderr
                            })
                            print(f"❌ {frontend_dir.name}: FAIL")
                    else:
                        print(f"⚠️  No lint script in {frontend_dir.name}")

        self.test_results["frontend_linting"] = lint_results
        return all(result["status"] == "PASS" for result in lint_results)

    def test_backend_functionality(self):
        """ทดสอบ backend functionality"""
        print("🔧 Testing Backend Functionality...")

        # Start backend server
        backend_process = self.start_backend_server()
        if not backend_process:
            return False

        time.sleep(3)  # Wait for server to start

        backend_tests = []

        # Test health endpoint
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                backend_tests.append({
                    "test": "health_check",
                    "status": "PASS",
                    "response_time": response.elapsed.total_seconds()
                })
                print("✅ Health check: PASS")
            else:
                backend_tests.append({
                    "test": "health_check",
                    "status": "FAIL",
                    "error": f"Status code: {response.status_code}"
                })
                print(f"❌ Health check: FAIL ({response.status_code})")
        except Exception as e:
            backend_tests.append({
                "test": "health_check",
                "status": "FAIL",
                "error": str(e)
            })
            print(f"❌ Health check: FAIL ({e})")

        # Stop backend server
        backend_process.terminate()
        backend_process.wait()

        self.test_results["backend_tests"] = backend_tests
        return all(test["status"] == "PASS" for test in backend_tests)

    def start_backend_server(self):
        """เริ่ม backend server สำหรับทดสอบ"""
        try:
            backend_dir = self.project_root / "services" / "local-rag"
            if backend_dir.exists():
                return subprocess.Popen(
                    [sys.executable, "simple_server.py"],
                    cwd=backend_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
        return None

    def test_build_process(self):
        """ทดสอบการ build"""
        print("🏗️ Testing Build Process...")

        # Test frontend build
        frontend_dir = self.project_root / "packages" / "frontend"
        if frontend_dir.exists():
            stdout, stderr = self.run_command(
                ["npm", "run", "build"],
                cwd=frontend_dir
            )
            if stdout is not None:
                print("✅ Frontend build: PASS")
                frontend_build = {"status": "PASS", "output": stdout}
            else:
                print("❌ Frontend build: FAIL")
                frontend_build = {"status": "FAIL", "error": stderr}
        else:
            frontend_build = {"status": "SKIP", "reason": "Directory not found"}

        # Test Craft IDE build
        craft_dir = self.project_root / "craft-ide"
        if craft_dir.exists():
            stdout, stderr = self.run_command(
                ["npm", "run", "build"],
                cwd=craft_dir
            )
            if stdout is not None:
                print("✅ Craft IDE build: PASS")
                craft_build = {"status": "PASS", "output": stdout}
            else:
                print("❌ Craft IDE build: FAIL")
                craft_build = {"status": "FAIL", "error": stderr}
        else:
            craft_build = {"status": "SKIP", "reason": "Directory not found"}

        self.test_results["build_tests"] = {
            "frontend": frontend_build,
            "craft_ide": craft_build
        }

        return (frontend_build.get("status") == "PASS" and
                craft_build.get("status") == "PASS")

    def generate_test_report(self):
        """สร้างรายงานการทดสอบ"""
        print("\n📊 Generating Test Report...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"test_report_{timestamp}.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results,
            "overall_status": self.calculate_overall_status()
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Test report saved: {report_file}")
        return report_file

    def calculate_overall_status(self):
        """คำนวณสถานะรวม"""
        all_passed = True

        for category, tests in self.test_results.items():
            if isinstance(tests, list):
                if not all(test.get("status") == "PASS" for test in tests):
                    all_passed = False
            elif isinstance(tests, dict):
                for test_name, test_result in tests.items():
                    if test_result.get("status") == "FAIL":
                        all_passed = False

        return "PASS" if all_passed else "FAIL"

    def deploy_to_test_environment(self):
        """deploy ไปยัง test environment"""
        print("🚀 Deploying to test environment...")

        try:
            # Create deployment package
            dist_dir = self.project_root / "test_dist"
            dist_dir.mkdir(exist_ok=True)

            # Copy necessary files
            import shutil

            # Copy executables if they exist
            release_dirs = [
                self.project_root / "packages" / "frontend" / "src-tauri" / "target" / "release",
                self.project_root / "craft-ide" / "src-tauri" / "target" / "release"
            ]

            deployed_files = []
            for release_dir in release_dirs:
                if release_dir.exists():
                    exe_files = list(release_dir.glob("*.exe"))
                    for exe_file in exe_files:
                        dest_file = dist_dir / exe_file.name
                        shutil.copy2(exe_file, dest_file)
                        deployed_files.append(str(dest_file))
                        print(f"✅ Deployed: {exe_file.name}")

            self.deployment_info = {
                "timestamp": datetime.now().isoformat(),
                "deployed_files": deployed_files,
                "deployment_path": str(dist_dir),
                "status": "SUCCESS"
            }

            print(f"✅ Deployment completed to: {dist_dir}")
            return True

        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            self.deployment_info = {
                "timestamp": datetime.now().isoformat(),
                "status": "FAILED",
                "error": str(e)
            }
            return False

    def save_deployment_info(self):
        """บันทึกข้อมูลการ deployment"""
        if self.deployment_info:
            deployment_file = self.project_root / "deployment_info.json"
            with open(deployment_file, "w", encoding="utf-8") as f:
                json.dump(self.deployment_info, f, indent=2)
            print(f"✅ Deployment info saved: {deployment_file}")

    def run_automated_pipeline(self):
        """รัน pipeline อัตโนมัติทั้งหมด"""
        print("🤖 Starting Automated Testing and Deployment Pipeline")
        print("=" * 60)

        pipeline_steps = [
            ("Frontend Linting", self.test_frontend_linting),
            ("Backend Functionality", self.test_backend_functionality),
            ("Build Process", self.test_build_process)
        ]

        all_passed = True

        for step_name, step_function in pipeline_steps:
            print(f"\n🔄 Running: {step_name}")
            print("-" * 40)

            if not step_function():
                all_passed = False
                print(f"❌ {step_name} failed")

                # Stop pipeline on failure
                print("🛑 Pipeline stopped due to failure")
                break
            else:
                print(f"✅ {step_name} passed")

        # Generate test report
        report_file = self.generate_test_report()

        if all_passed:
            print("\n🎉 All tests passed! Starting deployment...")
            if self.deploy_to_test_environment():
                self.save_deployment_info()
                print("\n✅ Pipeline completed successfully!")
                return True
            else:
                print("\n❌ Deployment failed")
                return False
        else:
            print("\n❌ Pipeline failed - some tests did not pass")
            return False

def main():
    tester = AutomatedTester()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "lint":
            tester.test_frontend_linting()
        elif command == "backend":
            tester.test_backend_functionality()
        elif command == "build":
            tester.test_build_process()
        elif command == "report":
            tester.generate_test_report()
        elif command == "deploy":
            if tester.deploy_to_test_environment():
                tester.save_deployment_info()
        elif command == "pipeline":
            success = tester.run_automated_pipeline()
            sys.exit(0 if success else 1)
        else:
            print("Usage: python test_and_deploy.py [lint|backend|build|report|deploy|pipeline]")
            print("  lint     - Test frontend linting")
            print("  backend  - Test backend functionality")
            print("  build    - Test build process")
            print("  report   - Generate test report")
            print("  deploy   - Deploy to test environment")
            print("  pipeline - Run full automated pipeline")
    else:
        # Run full pipeline by default
        success = tester.run_automated_pipeline()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
