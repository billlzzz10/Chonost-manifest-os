"""
Test script for Local RAG API
"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Local RAG API...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Add sample documents
    try:
        response = requests.post(f"{base_url}/api/rag/test/add-sample")
        print(f"✅ Add sample documents: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Add sample documents failed: {e}")
    
    # Test 3: Get RAG info
    try:
        response = requests.get(f"{base_url}/api/rag/info")
        print(f"✅ Get RAG info: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Get RAG info failed: {e}")
    
    # Test 4: Search documents
    try:
        response = requests.get(f"{base_url}/api/rag/search?query=Trinity Layout&limit=3")
        print(f"✅ Search documents: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Search documents failed: {e}")
    
    # Test 5: Get all documents
    try:
        response = requests.get(f"{base_url}/api/rag/documents")
        print(f"✅ Get all documents: {response.status_code} - {len(response.json())} documents")
    except Exception as e:
        print(f"❌ Get all documents failed: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    test_api()
