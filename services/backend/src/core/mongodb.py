#!/usr/bin/env python3
"""
MongoDB connection and utilities for Chonost
"""

import motor.motor_asyncio
from pymongo import MongoClient
from typing import Optional
from core.config import settings

class MongoDBManager:
    """
    A manager for handling MongoDB connections.

    This class provides methods for connecting to and disconnecting from a
    MongoDB database, as well as for getting synchronous and asynchronous
    clients and collections.

    Attributes:
        client (Optional[motor.motor_asyncio.AsyncIOMotorClient]): The asynchronous
                                                                   client.
        database (Optional[motor.motor_asyncio.AsyncIOMotorDatabase]): The
                                                                        database.
        sync_client (Optional[MongoClient]): The synchronous client.
    """
    
    def __init__(self):
        """Initializes the MongoDBManager."""
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
        self.sync_client: Optional[MongoClient] = None
    
    async def connect(self):
        """Connects to the MongoDB database."""
        try:
            mongo_url = settings.get_mongodb_url()
            self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            self.database = self.client[settings.MONGODB_DATABASE]

            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {settings.MONGODB_DATABASE}")

        except Exception as e:
            print(f"❌ MongoDB connection failed ({settings.get_sanitized_mongodb_url()}): {e}")
            raise
    
    async def disconnect(self):
        """Disconnects from the MongoDB database."""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    def get_sync_client(self) -> MongoClient:
        """
        Gets a synchronous MongoDB client.

        Returns:
            MongoClient: A synchronous MongoDB client.
        """
        if not self.sync_client:
            mongo_url = settings.get_mongodb_url()
            self.sync_client = MongoClient(mongo_url)
        return self.sync_client
    
    def get_collection(self, collection_name: str):
        """
        Gets a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            A MongoDB collection.
        """
        if self.database is None:
            raise RuntimeError("MongoDB not connected")
        return self.database[collection_name]

# Global MongoDB manager instance
mongodb_manager = MongoDBManager()

async def get_mongodb():
    """
    A dependency to get the MongoDB database.

    This function is used as a dependency in FastAPI routes to get the
    MongoDB database connection.

    Returns:
        The MongoDB database.
    """
    if mongodb_manager.database is None:
        await mongodb_manager.connect()
    return mongodb_manager.database

def get_mongodb_collection(collection_name: str):
    """
    Gets a MongoDB collection.

    Args:
        collection_name (str): The name of the collection.

    Returns:
        A MongoDB collection.
    """
    if mongodb_manager.database is None:
        raise RuntimeError("MongoDB not connected")
    return mongodb_manager.database[collection_name]
