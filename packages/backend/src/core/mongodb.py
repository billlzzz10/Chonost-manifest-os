#!/usr/bin/env python3
"""
MongoDB connection and utilities for Chonost
"""

import motor.motor_asyncio
from pymongo import MongoClient
from typing import Optional
from core.config import settings

class MongoDBManager:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.sync_client: Optional[MongoClient] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {settings.MONGODB_DATABASE}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    def get_sync_client(self) -> MongoClient:
        """Get synchronous MongoDB client"""
        if not self.sync_client:
            self.sync_client = MongoClient(settings.MONGODB_URL)
        return self.sync_client
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        if self.database is None:
            raise RuntimeError("MongoDB not connected")
        return self.database[collection_name]

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()

async def get_mongodb():
    """Dependency to get MongoDB database"""
    if mongodb_manager.database is None:
        await mongodb_manager.connect()
    return mongodb_manager.database

def get_mongodb_collection(collection_name: str):
    """Get MongoDB collection"""
    if mongodb_manager.database is None:
        raise RuntimeError("MongoDB not connected")
    return mongodb_manager.database[collection_name]
