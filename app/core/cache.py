"""
Simple in-memory caching layer for frequently accessed data
"""
import time
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple in-memory cache with TTL support
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            self.misses += 1
            return None
        
        value, expiry = self._cache[key]
        
        # Check if expired
        if time.time() > expiry:
            del self._cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f'{hit_rate:.2f}%',
            'size': len(self._cache),
            'total_requests': total
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        now = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if now > expiry
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


# Global cache instance
_cache = SimpleCache(default_ttl=300)  # 5 minutes default


def cached(ttl: Optional[int] = None, key_prefix: str = ''):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:"
            cache_key += _cache._generate_key(*args, **kwargs)
            
            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            
            return result
        
        # Add cache control methods to wrapped function
        wrapper.cache_clear = lambda: _cache.clear()
        wrapper.cache_stats = lambda: _cache.get_stats()
        
        return wrapper
    
    return decorator


def invalidate_cache(pattern: Optional[str] = None) -> int:
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Pattern to match (None = clear all)
    
    Returns:
        Number of entries cleared
    """
    if pattern is None:
        size = len(_cache._cache)
        _cache.clear()
        return size
    
    # Simple pattern matching (contains)
    to_delete = [
        key for key in _cache._cache.keys()
        if pattern in key
    ]
    
    for key in to_delete:
        _cache.delete(key)
    
    logger.info(f"Invalidated {len(to_delete)} cache entries matching '{pattern}'")
    return len(to_delete)


def get_cache_stats() -> dict:
    """Get global cache statistics"""
    return _cache.get_stats()
