#!/usr/bin/env python3
"""
Start Services for Phase 4 Validation
เริ่มต้น backend และ frontend services สำหรับการ validate
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path
from typing import Dict, Any

class ServiceStarter:
    """Starter for services needed for validation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_process = None
        self.frontend_process = None
        self.is_running = False
        
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        try:
            import requests
            print("✅ Requests library found")
            return True
        except ImportError:
            print("❌ Missing requests library")
            print("Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
            return True
    
    def start_backend_server(self) -> bool:
        """Start backend server"""
        try:
            backend_dir = self.project_root / "services" / "backend"
            main_file = backend_dir / "src" / "main.py"
            
            if not main_file.exists():
                print(f"❌ Backend main.py not found: {main_file}")
                return False
            
            print("🚀 Starting backend server...")
            self.backend_process = subprocess.Popen([
                sys.executable, str(main_file),
                "--host", "0.0.0.0",
                "--port", "8000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started on http://localhost:8000")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Backend server failed to start:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False
    
    def start_frontend_server(self) -> bool:
        """Start frontend server (simulated)"""
        try:
            frontend_dir = self.project_root / "services" / "frontend" / "web"
            
            if not frontend_dir.exists():
                print(f"❌ Frontend directory not found: {frontend_dir}")
                return False
            
            print("🚀 Starting frontend server (simulated)...")
            # For now, we'll simulate the frontend server
            # In a real scenario, you would start the React development server
            print("✅ Frontend server simulated on http://localhost:3000")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend server: {e}")
            return False
    
    def wait_for_services(self, timeout: int = 30) -> bool:
        """Wait for services to be ready"""
        print(f"⏳ Waiting for services to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        backend_ready = False
        frontend_ready = False
        
        while time.time() - start_time < timeout:
            # Check backend
            if not backend_ready:
                try:
                    response = requests.get("http://localhost:8000/api/integrated/system/health", timeout=2)
                    if response.status_code == 200:
                        backend_ready = True
                        print("✅ Backend service is ready")
                except:
                    pass
            
            # Check frontend (simulated)
            if not frontend_ready:
                try:
                    response = requests.get("http://localhost:3000", timeout=2)
                    if response.status_code == 200:
                        frontend_ready = True
                        print("✅ Frontend service is ready")
                except:
                    pass
            
            if backend_ready and frontend_ready:
                print("🎉 All services are ready!")
                return True
            
            time.sleep(1)
        
        print("⚠️ Timeout waiting for services")
        return False
    
    def stop_services(self):
        """Stop all services"""
        if self.backend_process:
            print("🛑 Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            print("✅ Backend server stopped")
        
        if self.frontend_process:
            print("🛑 Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            print("✅ Frontend server stopped")
    
    def run_services(self, timeout: int = 30):
        """Run services for validation"""
        if not self.check_dependencies():
            print("❌ Failed to check dependencies")
            return False
        
        if not self.start_backend_server():
            print("❌ Failed to start backend server")
            return False
        
        if not self.start_frontend_server():
            print("❌ Failed to start frontend server")
            return False
        
        if not self.wait_for_services(timeout):
            print("❌ Services not ready within timeout")
            return False
        
        self.is_running = True
        
        try:
            print("\n🔄 Services are running. Press Ctrl+C to stop.")
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            self.stop_services()
        
        return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Start services for Phase 4 validation")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout for services to be ready (seconds)")
    parser.add_argument("--validate-only", action="store_true", help="Start services for validation only")
    
    args = parser.parse_args()
    
    starter = ServiceStarter()
    
    if args.validate_only:
        # Start services for validation
        if starter.run_services(args.timeout):
            print("✅ Services started successfully for validation")
            sys.exit(0)
        else:
            print("❌ Failed to start services")
            sys.exit(1)
    else:
        # Start services normally
        starter.run_services(args.timeout)

if __name__ == "__main__":
    main()
