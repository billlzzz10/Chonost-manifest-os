#!/usr/bin/env python3
"""
Backend Server Starter for Chonost System
เริ่มต้น backend server สำหรับทดสอบ API endpoints
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class BackendServerStarter:
    """Starter for Chonost backend server"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "services" / "backend"
        self.server_process = None
        self.is_running = False
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        try:
            import flask
            import flask_cors
            print("✅ Flask dependencies found")
            return True
        except ImportError as e:
            print(f"❌ Missing Flask dependency: {e}")
            print("Installing dependencies...")
            return self.install_dependencies()
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        try:
            requirements_file = self.backend_dir / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True)
                print("✅ Dependencies installed successfully")
                return True
            else:
                print("❌ requirements.txt not found")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def start_server(self, port: int = 8000) -> bool:
        """Start the backend server"""
        try:
            # Change to backend directory
            os.chdir(self.backend_dir)
            
            # Check if main.py exists
            main_file = self.backend_dir / "src" / "main.py"
            if not main_file.exists():
                print(f"❌ Main file not found: {main_file}")
                return False
            
            # Start the server
            print(f"🚀 Starting Chonost backend server on port {port}...")
            self.server_process = subprocess.Popen([
                sys.executable, str(main_file),
                "--host", "0.0.0.0",
                "--port", str(port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.is_running = True
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if server is running
            if self.server_process.poll() is None:
                print(f"✅ Backend server started successfully on http://localhost:{port}")
                print("📋 Available endpoints:")
                print(f"   - Health Check: GET http://localhost:{port}/api/integrated/system/health")
                print(f"   - Manuscripts: GET/POST http://localhost:{port}/api/integrated/manuscripts")
                print(f"   - AI Analysis: POST http://localhost:{port}/api/integrated/ai/analyze-characters")
                print(f"   - Writing Assistant: POST http://localhost:{port}/api/integrated/ai/writing-assistant")
                print(f"   - Analytics: GET http://localhost:{port}/api/integrated/analytics/overview")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ Server failed to start:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the backend server"""
        if self.server_process and self.is_running:
            print("🛑 Stopping backend server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.is_running = False
            print("✅ Backend server stopped")
    
    def run_with_monitoring(self, port: int = 8000):
        """Run server with monitoring"""
        if not self.check_dependencies():
            print("❌ Failed to check/install dependencies")
            return False
        
        if not self.start_server(port):
            print("❌ Failed to start server")
            return False
        
        try:
            print("\n🔄 Server is running. Press Ctrl+C to stop.")
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            self.stop_server()
        
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Chonost backend server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on (default: 8000)")
    parser.add_argument("--test-only", action="store_true", help="Start server for testing only")
    
    args = parser.parse_args()
    
    starter = BackendServerStarter()
    
    if args.test_only:
        # Start server for testing
        if starter.run_with_monitoring(args.port):
            print("✅ Server test completed successfully")
            sys.exit(0)
        else:
            print("❌ Server test failed")
            sys.exit(1)
    else:
        # Start server normally
        starter.run_with_monitoring(args.port)

if __name__ == "__main__":
    main()
