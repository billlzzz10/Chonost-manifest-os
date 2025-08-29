#!/usr/bin/env python3
"""
Test MongoDB Connection Script
ทดสอบการเชื่อมต่อ MongoDB
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "packages" / "backend" / "src"
sys.path.insert(0, str(backend_src))

from core.mongodb import mongodb_manager
from core.config import settings

async def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB Connection...")
    print(f"URL: {settings.MONGODB_URL}")
    print(f"Database: {settings.MONGODB_DATABASE}")
    
    try:
        # Connect to MongoDB
        await mongodb_manager.connect()
        print("✅ MongoDB connection successful!")
        
        # Test basic operations
        collection = mongodb_manager.get_collection("test")
        
        # Insert test document
        test_doc = {
            "name": "test_document",
            "message": "Hello from Chonost!",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = await collection.insert_one(test_doc)
        print(f"✅ Inserted test document with ID: {result.inserted_id}")
        
        # Find test document
        found_doc = await collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print(f"✅ Found document: {found_doc['name']}")
        
        # Delete test document
        await collection.delete_one({"_id": result.inserted_id})
        print("✅ Deleted test document")
        
        # Disconnect
        await mongodb_manager.disconnect()
        print("✅ MongoDB test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def test_mongodb_collections():
    """Test MongoDB collections"""
    print("\n📋 Testing MongoDB Collections...")
    
    try:
        await mongodb_manager.connect()
        
        # List collections
        collections = await mongodb_manager.database.list_collection_names()
        print(f"📁 Available collections: {collections}")
        
        # Create test collection if not exists
        test_collection = mongodb_manager.get_collection("chonost_documents")
        
        # Insert sample data
        sample_docs = [
            {
                "title": "Sample Document 1",
                "content": "This is a sample document for testing",
                "type": "text",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "title": "Sample Document 2", 
                "content": "Another sample document",
                "type": "text",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        result = await test_collection.insert_many(sample_docs)
        print(f"✅ Inserted {len(result.inserted_ids)} sample documents")
        
        # Count documents
        count = await test_collection.count_documents({})
        print(f"📊 Total documents in collection: {count}")
        
        # Find documents
        cursor = test_collection.find({})
        docs = await cursor.to_list(length=10)
        print(f"📄 Found {len(docs)} documents")
        
        for doc in docs:
            print(f"  - {doc['title']}")
        
        await mongodb_manager.disconnect()
        print("✅ MongoDB collections test completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB collections test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 MongoDB Connection Test")
    print("=" * 50)
    
    # Test basic connection
    connection_success = await test_mongodb_connection()
    
    if connection_success:
        # Test collections
        await test_mongodb_collections()
    
    print("\n" + "=" * 50)
    if connection_success:
        print("🎉 All MongoDB tests passed!")
    else:
        print("❌ MongoDB tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
