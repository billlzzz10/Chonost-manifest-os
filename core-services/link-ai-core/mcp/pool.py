"""
MCP Connection Pool.
This module provides a connection pool for MCP servers, supporting various transport layers.
"""

import asyncio
import time
from collections import OrderedDict
from typing import Dict, Optional, Tuple

from models import MCPServer
from mcp.client import MCPClient
from config import Settings
from utils.log import get_logger

# Initialize settings
settings = Settings()
logger = get_logger(__name__)

class MCPPool:
    """
    A connection pool for MCP servers that supports multiple transport types.
    This class manages a pool of MCP clients to avoid the overhead of creating
    a new client for every request. It also handles client expiration and eviction.
    """
    
    def __init__(self, maxsize: int = None, ttl_seconds: int = None):
        """
        Initializes the MCP pool.
        """
        self.maxsize = maxsize or settings.mcp_pool_max
        self.ttl_seconds = ttl_seconds or settings.mcp_ttl_seconds
        
        self._pool: OrderedDict[str, Tuple[MCPClient, float, float]] = OrderedDict()
        self._lock = asyncio.Lock()
        self._stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0
        }

    async def get(self, key: str, server: MCPServer) -> MCPClient:
        """
        Gets an MCP client from the pool or creates a new one.
        """
        async with self._lock:
            now = time.time()
            
            if key in self._pool:
                client, created_ts, last_used_ts = self._pool.pop(key)
                
                if now - created_ts <= self.ttl_seconds:
                    self._pool[key] = (client, created_ts, now)
                    self._stats["pool_hits"] += 1
                    logger.debug(f"Pool hit for {key}")
                    return client
                else:
                    logger.debug(f"Client {key} expired, stopping")
                    await client.stop()
                    self._stats["active_connections"] -= 1
            
            try:
                client = MCPClient(server)
                await client.start()
                
                self._pool[key] = (client, now, now)
                self._stats["total_connections"] += 1
                self._stats["active_connections"] += 1
                self._stats["pool_misses"] += 1
                
                logger.info(f"Created new MCP client for {key} (transport: {server.kind})")
                
                while len(self._pool) > self.maxsize:
                    oldest_key, (oldest_client, _, _) = self._pool.popitem(last=False)
                    logger.debug(f"Pool full, removing oldest client: {oldest_key}")
                    await oldest_client.stop()
                    self._stats["active_connections"] -= 1
                
                return client
                
            except Exception as e:
                self._stats["failed_connections"] += 1
                logger.error(f"Failed to create MCP client for {key}: {e}")
                raise

    async def release(self, key: str) -> None:
        """
        Releases a client back to the pool.
        """
        logger.debug(f"Client {key} released back to pool")

    async def remove(self, key: str) -> None:
        """
        Removes a client from the pool.
        """
        async with self._lock:
            if key in self._pool:
                client, _, _ = self._pool.pop(key)
                await client.stop()
                self._stats["active_connections"] -= 1
                logger.info(f"Removed client {key} from pool")

    async def clear(self) -> None:
        """Clears the entire pool, stopping all clients."""
        async with self._lock:
            logger.info("Clearing MCP pool")
            for key, (client, _, _) in self._pool.items():
                await client.stop()
            
            self._pool.clear()
            self._stats["active_connections"] = 0

    async def health_check(self) -> Dict[str, any]:
        """
        Checks the health of the clients in the pool.
        """
        async with self._lock:
            healthy_clients = 0
            total_clients = len(self._pool)
            
            for key, (client, created_ts, last_used_ts) in list(self._pool.items()):
                try:
                    if not client.initialized:
                        logger.warning(f"Unhealthy client {key} detected, removing")
                        await client.stop()
                        self._pool.pop(key, None)
                        self._stats["active_connections"] -= 1
                    else:
                        healthy_clients += 1
                        
                except Exception as e:
                    logger.error(f"Error checking client {key} health: {e}")
                    self._pool.pop(key, None)
                    self._stats["active_connections"] -= 1
            
            return {
                "total_clients": total_clients,
                "healthy_clients": healthy_clients,
                "pool_size": len(self._pool),
                "max_size": self.maxsize,
                "ttl_seconds": self.ttl_seconds,
                "stats": self._stats.copy()
            }

    def get_stats(self) -> Dict[str, any]:
        """
        Gets the statistics for the pool.
        """
        return {
            "pool_size": len(self._pool),
            "max_size": self.maxsize,
            "ttl_seconds": self.ttl_seconds,
            **self._stats
        }

    async def close(self) -> None:
        """Closes the pool and stops all clients."""
        logger.info("Closing MCP pool")
        await self.clear()

# Global pool instance
pool = MCPPool()