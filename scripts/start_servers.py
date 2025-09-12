"""
Startup Script for Chonost Desktop App
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_frontend():
    """Start Frontend Development Server"""
    print("🌐 Starting Frontend Development Server...")
    
    frontend_dir = Path("packages/frontend")
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Start npm dev server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Frontend server started (PID: {process.pid})")
        print("📡 Frontend will be available at http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def start_backend():
    """Start Backend API Server"""
    print("🔧 Starting Backend API Server...")
    
    backend_dir = Path("services/local-rag")
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        return False
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start simple server
        process = subprocess.Popen(
            [sys.executable, "simple_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Backend server started (PID: {process.pid})")
        print("📡 Backend will be available at http://localhost:8000")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def main():
    print("🚀 Chonost Desktop App Startup")
    print("=" * 40)
    
    # Get project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Start servers
    frontend_process = start_frontend()
    time.sleep(2)  # Wait a bit
    
    backend_process = start_backend()
    time.sleep(2)  # Wait a bit
    
    if frontend_process and backend_process:
        print("\n" + "=" * 40)
        print("🎯 Both servers started successfully!")
        print("📝 Next steps:")
        print("1. Open browser to http://localhost:3000")
        print("2. Test The Trinity Layout")
        print("3. Test Editor/Whiteboard switching")
        print("4. Test RAG search at http://localhost:8000/api/rag/search")
        print("\n⏳ Press Ctrl+C to stop servers...")
        
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            if frontend_process:
                frontend_process.terminate()
            if backend_process:
                backend_process.terminate()
            print("✅ Servers stopped")
    else:
        print("\n❌ Failed to start one or more servers")
        sys.exit(1)

if __name__ == "__main__":
    main()
