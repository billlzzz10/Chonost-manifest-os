"""
MCP Connection Pool
จัดการ connection pool สำหรับ MCP servers รองรับ transport หลายแบบ
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
    """Connection pool สำหรับ MCP servers รองรับ transport หลายแบบ"""
    
    def __init__(self, maxsize: int = None, ttl_seconds: int = None):
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
        ดึง MCP client จาก pool หรือสร้างใหม่
        
        Args:
            key: Pool key (usually server name)
            server: MCPServer configuration
            
        Returns:
            MCPClient instance
        """
        async with self._lock:
            now = time.time()
            
            # ตรวจสอบว่ามี client ใน pool หรือไม่
            if key in self._pool:
                client, created_ts, last_used_ts = self._pool.pop(key)
                
                # ตรวจสอบ TTL
                if now - created_ts <= self.ttl_seconds:
                    # Client ยังใช้งานได้ - อัปเดต timestamp และย้ายไปท้าย queue
                    self._pool[key] = (client, created_ts, now)
                    self._stats["pool_hits"] += 1
                    logger.debug(f"Pool hit for {key}")
                    return client
                else:
                    # Client หมดอายุ - หยุดและลบ
                    logger.debug(f"Client {key} expired, stopping")
                    await client.stop()
                    self._stats["active_connections"] -= 1
            
            # สร้าง client ใหม่
            try:
                client = MCPClient(server)
                await client.start()
                
                # เพิ่มเข้า pool
                self._pool[key] = (client, now, now)
                self._stats["total_connections"] += 1
                self._stats["active_connections"] += 1
                self._stats["pool_misses"] += 1
                
                logger.info(f"Created new MCP client for {key} (transport: {server.kind})")
                
                # ตรวจสอบ pool size limit
                while len(self._pool) > self.maxsize:
                    # ลบ client ที่เก่าที่สุด
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
        คืน client กลับไปยัง pool (ไม่ทำอะไรใน implementation นี้)
        Client จะถูกเก็บไว้ใน pool จนกว่าจะหมดอายุ
        """
        logger.debug(f"Client {key} released back to pool")

    async def remove(self, key: str) -> None:
        """
        ลบ client ออกจาก pool
        
        Args:
            key: Pool key
        """
        async with self._lock:
            if key in self._pool:
                client, _, _ = self._pool.pop(key)
                await client.stop()
                self._stats["active_connections"] -= 1
                logger.info(f"Removed client {key} from pool")

    async def clear(self) -> None:
        """ล้าง pool ทั้งหมด"""
        async with self._lock:
            logger.info("Clearing MCP pool")
            for key, (client, _, _) in self._pool.items():
                await client.stop()
            
            self._pool.clear()
            self._stats["active_connections"] = 0

    async def health_check(self) -> Dict[str, any]:
        """ตรวจสอบสุขภาพของ pool"""
        async with self._lock:
            healthy_clients = 0
            total_clients = len(self._pool)
            
            for key, (client, created_ts, last_used_ts) in self._pool.items():
                try:
                    # ตรวจสอบว่า client ยังทำงานอยู่หรือไม่
                    if client.initialized:
                        healthy_clients += 1
                    else:
                        # Client ไม่ทำงาน - ลบออก
                        logger.warning(f"Unhealthy client {key} detected, removing")
                        await client.stop()
                        self._pool.pop(key, None)
                        self._stats["active_connections"] -= 1
                        
                except Exception as e:
                    logger.error(f"Error checking client {key} health: {e}")
                    # ลบ client ที่มีปัญหา
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
        """ดึงสถิติของ pool"""
        return {
            "pool_size": len(self._pool),
            "max_size": self.maxsize,
            "ttl_seconds": self.ttl_seconds,
            **self._stats
        }

    async def close(self) -> None:
        """ปิด pool และหยุด clients ทั้งหมด"""
        logger.info("Closing MCP pool")
        await self.clear()

# Global pool instance
pool = MCPPool()
