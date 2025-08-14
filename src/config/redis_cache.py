import json
import pickle
from typing import Any, Optional, Union, Dict, List
from functools import wraps
import asyncio
import logging

import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError

from .settings import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager with async support and error handling."""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._is_connected = False
        
    async def connect(self) -> None:
        """Establish Redis connection."""
        try:
            # Parse Redis URL to get connection details
            redis_url = str(settings.REDIS_URL)
            
            if settings.REDIS_USE_SSL:
                # Use SSL connection
                self._connection_pool = redis.ConnectionPool.from_url(
                    redis_url.replace("redis://", "rediss://"),
                    max_connections=20,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                )
            else:
                # Use regular connection
                self._connection_pool = redis.ConnectionPool.from_url(
                    redis_url,
                    max_connections=20,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                )
            
            self._redis_client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._redis_client.ping()
            self._is_connected = True
            logger.info("Redis connection established successfully")
            
        except (ConnectionError, RedisError) as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
            self._is_connected = False
            logger.info("Redis connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._is_connected
    
    async def _ensure_connection(self) -> None:
        """Ensure Redis connection is established."""
        if not self._is_connected or not self._redis_client:
            await self.connect()
    
    def _make_key(self, key: str) -> str:
        """Create a cache key with prefix."""
        return f"{settings.CACHE_PREFIX}{key}"
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            await self._ensure_connection()
            cache_key = self._make_key(key)
            value = await self._redis_client.get(cache_key)
            
            if value is None:
                return default
            
            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value)
                except (pickle.UnpicklingError, TypeError):
                    return value.decode('utf-8') if isinstance(value, bytes) else value
                    
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis get error: {e}")
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            await self._ensure_connection()
            cache_key = self._make_key(key)
            
            if serialize:
                # Try JSON first, fallback to pickle
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = value
            
            ttl = ttl or settings.CACHE_TTL
            result = await self._redis_client.setex(cache_key, ttl, serialized_value)
            return bool(result)
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            await self._ensure_connection()
            cache_key = self._make_key(key)
            result = await self._redis_client.delete(cache_key)
            return bool(result)
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            await self._ensure_connection()
            cache_key = self._make_key(key)
            result = await self._redis_client.exists(cache_key)
            return bool(result)
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        try:
            await self._ensure_connection()
            cache_key = self._make_key(key)
            result = await self._redis_client.expire(cache_key, ttl)
            return bool(result)
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis expire error: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL for a key."""
        try:
            await self._ensure_connection()
            cache_key = self._make_key(key)
            result = await self._redis_client.ttl(cache_key)
            return result
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis TTL error: {e}")
            return -1
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern."""
        try:
            await self._ensure_connection()
            cache_pattern = self._make_key(pattern)
            keys = await self._redis_client.keys(cache_pattern)
            
            if keys:
                result = await self._redis_client.delete(*keys)
                return result
            return 0
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis clear pattern error: {e}")
            return 0
    
    async def clear_all(self) -> bool:
        """Clear all cache keys."""
        try:
            await self._ensure_connection()
            pattern = f"{settings.CACHE_PREFIX}*"
            keys = await self._redis_client.keys(pattern)
            
            if keys:
                await self._redis_client.delete(*keys)
            
            return True
            
        except (RedisError, ConnectionError) as e:
            logger.error(f"Redis clear all error: {e}")
            return False


# Global Redis cache instance
redis_cache = RedisCache()


def cache_result(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    key_builder: Optional[callable] = None
):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key building
                func_name = func.__name__
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{key_prefix}{func_name}:{hash(args_str)}"
            
            # Try to get from cache
            cached_result = await redis_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key building
                func_name = func.__name__
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{key_prefix}{func_name}:{hash(args_str)}"
            
            # Try to get from cache
            loop = asyncio.get_event_loop()
            cached_result = loop.run_until_complete(redis_cache.get(cache_key))
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            loop.run_until_complete(redis_cache.set(cache_key, result, ttl))
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return wrapper
        else:
            return sync_wrapper
    
    return decorator


# Utility functions for common cache operations
async def get_cached_or_fetch(
    key: str,
    fetch_func: callable,
    ttl: Optional[int] = None,
    *args,
    **kwargs
) -> Any:
    """Get value from cache or fetch using provided function."""
    cached_value = await redis_cache.get(key)
    if cached_value is not None:
        return cached_value
    
    # Fetch new value
    if asyncio.iscoroutinefunction(fetch_func):
        value = await fetch_func(*args, **kwargs)
    else:
        value = fetch_func(*args, **kwargs)
    
    # Cache the result
    await redis_cache.set(key, value, ttl)
    return value


async def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate cache keys matching a pattern."""
    return await redis_cache.clear_pattern(pattern)


async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        await redis_cache._ensure_connection()
        info = await redis_cache._redis_client.info()
        
        return {
            "connected": redis_cache.is_connected,
            "redis_version": info.get("redis_version"),
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"connected": False, "error": str(e)}
