"""
MCP Connection Pool.
This module provides a connection pool for MCP servers, supporting various transport layers.
"""

import asyncio
import time
from collections import OrderedDict
from typing import Dict, Optional, Tuple
try:
    # Try unified backend path
    from ..models import MCPServer
    from .client import MCPClient
    from ..config import Settings
    from ..utils.log import get_logger

    # Initialize settings
    settings = Settings()
    logger = get_logger(__name__)

except ImportError:
    # Fallback for standalone usage
    from models import MCPServer
    from client import MCPClient

    # Simple settings fallback
    class SimpleSettings:
        mcp_pool_max = 4
        mcp_ttl_seconds = 300

    settings = SimpleSettings()

    # Simple logger fallback
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class MCPPool:
    """
    A connection pool for MCP servers that supports multiple transport types.

    This class manages a pool of MCP clients to avoid the overhead of creating
    a new client for every request. It also handles client expiration and eviction.
    """
    
    def __init__(self, maxsize: int = None, ttl_seconds: int = None):
        """
        Initializes the MCP pool.

        Args:
            maxsize (int, optional): The maximum number of clients to keep in the pool.
                                     Defaults to the value from settings.
            ttl_seconds (int, optional): The time-to-live for clients in seconds.
                                         Defaults to the value from settings.
        """
        self.maxsize = maxsize or settings.mcp_pool_max
        self.ttl_seconds = ttl_seconds or settings.mcp_ttl_seconds
        
        # Pool storage: key -> (client, timestamp, last_used)
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

        If a valid client for the given key exists in the pool, it is returned.
        Otherwise, a new client is created and added to the pool.

        Args:
            key (str): The pool key, which is typically the server name.
            server (MCPServer): The configuration for the MCP server.

        Returns:
            MCPClient: An MCP client instance.
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

        In this implementation, this method does nothing, as clients are kept
        in the pool until they expire.

        Args:
            key (str): The pool key.
        """
        logger.debug(f"Client {key} released back to pool")

    async def remove(self, key: str) -> None:
        """
        Removes a client from the pool.

        Args:
            key (str): The pool key.
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

        This method iterates through the clients in the pool, checks their status,
        and removes any unhealthy clients.

        Returns:
            Dict[str, any]: A dictionary containing the health check results.
        """
        async with self._lock:
            healthy_clients = 0
            total_clients = len(self._pool)
            
            for key, (client, created_ts, last_used_ts) in self._pool.items():
                try:
                    if client.initialized:
                        healthy_clients += 1
                    else:
                        logger.warning(f"Unhealthy client {key} detected, removing")
                        await client.stop()
                        self._pool.pop(key, None)
                        self._stats["active_connections"] -= 1
                        
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

        Returns:
            Dict[str, any]: A dictionary containing the pool's statistics.
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
