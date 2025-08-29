#!/usr/bin/env python3
"""
Simple Backend Server Starter for Chonost
เริ่มต้น backend server ที่ port 5000
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def start_backend_server():
    """Start the backend server"""
    print("🚀 Starting Chonost Backend Server...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "services" / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check if main.py exists
    main_py = backend_dir / "src" / "main.py"
    if not main_py.exists():
        print("❌ main.py not found!")
        return False
    
    print(f"✅ Backend directory: {backend_dir}")
    print(f"✅ Main file: {main_py}")
    
    try:
        # Start the server
        print("🔄 Starting Flask server on port 5000...")
        process = subprocess.Popen([
            sys.executable, "src/main.py"
        ], cwd=backend_dir)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Backend server started successfully!")
            print("🌐 Server URL: http://localhost:5000")
            print("📊 Health Check: http://localhost:5000/api/integrated/system/health")
            print("📝 Press Ctrl+C to stop the server")
            
            try:
                # Keep the server running
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")
            
            return True
        else:
            print("❌ Server failed to start!")
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    start_backend_server()
