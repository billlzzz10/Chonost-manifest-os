"""
Simple Test Script for Desktop App
"""

import time
import webbrowser
import requests

def test_frontend():
    """Test Frontend Development Server"""
    print("🌐 Testing Frontend...")
    
    try:
        # Try to open browser
        webbrowser.open('http://localhost:3000')
        print("✅ Frontend server should be running at http://localhost:3000")
        print("📝 Please check if The Trinity Layout is working:")
        print("   - Editor/Whiteboard switching")
        print("   - KnowledgeExplorer sidebar")
        print("   - AssistantPanel sidebar")
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")

def test_backend():
    """Test Backend API Server"""
    print("\n🔧 Testing Backend...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running")
            print(f"📊 Response: {response.json()}")
            
            # Test RAG functionality
            print("\n🔍 Testing RAG functionality...")
            
            # Add sample documents
            response = requests.post('http://localhost:8000/api/rag/test/add-sample')
            if response.status_code == 200:
                print("✅ Sample documents added")
                print(f"📄 {response.json()}")
            
            # Search documents
            response = requests.get('http://localhost:8000/api/rag/search?query=Trinity Layout&limit=3')
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Search working - Found {len(results)} results")
                for result in results:
                    print(f"   📝 {result['title']} (similarity: {result['similarity']:.2f})")
            
        else:
            print(f"❌ Backend API error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend API not running - please start the API server")
    except Exception as e:
        print(f"❌ Backend test failed: {e}")

def main():
    print("🚀 Chonost Desktop App Test")
    print("=" * 40)
    
    # Wait for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Test both frontend and backend
    test_frontend()
    test_backend()
    
    print("\n" + "=" * 40)
    print("🎯 Test Summary:")
    print("1. Frontend should be running at http://localhost:3000")
    print("2. Backend API should be running at http://localhost:8000")
    print("3. Check browser for The Trinity Layout")
    print("4. Test Editor/Whiteboard switching")
    print("5. Test RAG search functionality")

if __name__ == "__main__":
    main()
