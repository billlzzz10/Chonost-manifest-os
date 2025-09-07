#!/usr/bin/env python3
"""
Chonost Integration Test Script
ทดสอบการรวมเครื่องมือทั้ง 3 แพลตฟอร์มกับโปรเจกต์ Chonost
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "chonost-unified" / "backend"))

class ChonostIntegrationTest:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []

    async def test_file_operations(self):
        """Test integrated file operations"""
        print("[TEST] Testing File Operations Integration...")

        # Test Kilo Code file operations
        test_file = self.project_root / "test_integration.txt"
        try:
            # Create test file
            test_file.write_text("Integration test content")

            # Read file
            content = test_file.read_text()
            assert content == "Integration test content"

            # Clean up
            test_file.unlink()

            self.test_results.append({
                'test': 'file_operations',
                'status': 'passed',
                'platform': 'kilo_code'
            })
            print("✅ Kilo Code file operations: PASSED")

        except Exception as e:
            self.test_results.append({
                'test': 'file_operations',
                'status': 'failed',
                'platform': 'kilo_code',
                'error': str(e)
            })
            print(f"❌ Kilo Code file operations: FAILED - {e}")

    async def test_backend_integration(self):
        """Test backend API integration"""
        print("🧪 Testing Backend API Integration...")

        try:
            # Import backend components
            from backend.main import app  # type: ignore

            # Test health endpoint
            from fastapi.testclient import TestClient  # type: ignore
            client = TestClient(app)

            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

            self.test_results.append({
                'test': 'backend_api',
                'status': 'passed',
                'platform': 'backend'
            })
            print("✅ Backend API integration: PASSED")

        except ImportError:
            self.test_results.append({
                'test': 'backend_api',
                'status': 'skipped',
                'platform': 'backend',
                'error': 'Backend dependencies not available'
            })
            print("⚠️ Backend API integration: SKIPPED - Dependencies not available")

        except Exception as e:
            self.test_results.append({
                'test': 'backend_api',
                'status': 'failed',
                'platform': 'backend',
                'error': str(e)
            })
            print(f"❌ Backend API integration: FAILED - {e}")

    async def test_frontend_integration(self):
        """Test frontend integration"""
        print("🧪 Testing Frontend Integration...")

        try:
            # Check if frontend dependencies are installed
            frontend_dir = self.project_root / "packages" / "frontend"
            if (frontend_dir / "node_modules").exists():
                self.test_results.append({
                    'test': 'frontend_deps',
                    'status': 'passed',
                    'platform': 'frontend'
                })
                print("✅ Frontend dependencies: INSTALLED")
            else:
                self.test_results.append({
                    'test': 'frontend_deps',
                    'status': 'failed',
                    'platform': 'frontend',
                    'error': 'node_modules not found'
                })
                print("❌ Frontend dependencies: NOT INSTALLED")

        except Exception as e:
            self.test_results.append({
                'test': 'frontend_deps',
                'status': 'failed',
                'platform': 'frontend',
                'error': str(e)
            })
            print(f"❌ Frontend integration: FAILED - {e}")

    async def test_cursor_integration(self):
        """Test Cursor rules integration"""
        print("🧪 Testing Cursor Integration...")

        try:
            # Check for .cursorrules
            cursorrules_file = self.project_root / "FileSystemMCP" / ".cursorrules"
            if cursorrules_file.exists():
                content = cursorrules_file.read_text()
                assert "Chonost Ecosystem" in content

                self.test_results.append({
                    'test': 'cursor_rules',
                    'status': 'passed',
                    'platform': 'cursor'
                })
                print("✅ Cursor rules: FOUND AND VALID")
            else:
                self.test_results.append({
                    'test': 'cursor_rules',
                    'status': 'failed',
                    'platform': 'cursor',
                    'error': '.cursorrules not found'
                })
                print("❌ Cursor rules: NOT FOUND")

        except Exception as e:
            self.test_results.append({
                'test': 'cursor_rules',
                'status': 'failed',
                'platform': 'cursor',
                'error': str(e)
            })
            print(f"❌ Cursor integration: FAILED - {e}")

    async def test_continue_integration(self):
        """Test Continue configuration"""
        print("🧪 Testing Continue Integration...")

        try:
            # Check Continue config
            continue_config = self.project_root / ".continue" / "config.yaml"
            if continue_config.exists():
                content = continue_config.read_text()
                assert "Chonost Ecosystem" in content

                self.test_results.append({
                    'test': 'continue_config',
                    'status': 'passed',
                    'platform': 'continue'
                })
                print("✅ Continue configuration: VALID")
            else:
                self.test_results.append({
                    'test': 'continue_config',
                    'status': 'failed',
                    'platform': 'continue',
                    'error': 'Continue config not found'
                })
                print("❌ Continue configuration: NOT FOUND")

        except Exception as e:
            self.test_results.append({
                'test': 'continue_config',
                'status': 'failed',
                'platform': 'continue',
                'error': str(e)
            })
            print(f"❌ Continue integration: FAILED - {e}")

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Chonost Integration Tests\n")

        await self.test_file_operations()
        await self.test_backend_integration()
        await self.test_frontend_integration()
        await self.test_cursor_integration()
        await self.test_continue_integration()

        print("\n📊 Test Results Summary:")
        print("=" * 50)

        passed = 0
        failed = 0
        skipped = 0

        for result in self.test_results:
            status = result['status']
            if status == 'passed':
                passed += 1
                print(f"✅ {result['test']} ({result['platform']}): PASSED")
            elif status == 'failed':
                failed += 1
                print(f"❌ {result['test']} ({result['platform']}): FAILED")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
            elif status == 'skipped':
                skipped += 1
                print(f"⚠️ {result['test']} ({result['platform']}): SKIPPED")
                if 'error' in result:
                    print(f"   Reason: {result['error']}")

        print("\n" + "=" * 50)
        print(f"📈 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Skipped: {skipped}")

        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        print(f"{success_rate:.1f}")
        if success_rate >= 80:
            print("🎉 Integration Status: EXCELLENT")
        elif success_rate >= 60:
            print("👍 Integration Status: GOOD")
        else:
            print("⚠️ Integration Status: NEEDS IMPROVEMENT")

        return success_rate >= 60

async def main():
    """Main test execution"""
    tester = ChonostIntegrationTest()
    success = await tester.run_all_tests()

    if success:
        print("\n🎯 Chonost Integration: SUCCESS")
        sys.exit(0)
    else:
        print("\n💥 Chonost Integration: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())