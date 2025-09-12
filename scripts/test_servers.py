"""
Test Script for Servers
"""

import time
import webbrowser
import requests  # pyright: ignore[reportMissingModuleSource]

def test_frontend():
    """Test Frontend Development Server"""
    print("🌐 Testing Frontend...")
    
    try:
        response = requests.get('http://localhost:1420', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running at http://localhost:1420")
            # Try to open browser
            webbrowser.open('http://localhost:1420')
            print("📝 Please check if The Trinity Layout is working:")
            print("   - Editor/Whiteboard switching")
            print("   - KnowledgeExplorer sidebar")
            print("   - AssistantPanel sidebar")
        else:
            print(f"❌ Frontend server error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server not running - please start the development server")
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
            
            # Get RAG info
            response = requests.get('http://localhost:8000/api/rag/info')
            if response.status_code == 200:
                info = response.json()
                print(f"✅ RAG info: {info['total_documents']} documents, {info['total_chunks']} chunks")
            
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
    time.sleep(3)
    
    # Test both frontend and backend
    test_frontend()
    test_backend()
    
    print("\n" + "=" * 40)
    print("🎯 Test Summary:")
    print("1. Frontend should be running at http://localhost:1420")
    print("2. Backend API should be running at http://localhost:8000")
    print("3. Check browser for The Trinity Layout")
    print("4. Test Editor/Whiteboard switching")
    print("5. Test RAG search functionality")

if __name__ == "__main__":
    main()
