"""
Cache Manager for NITROTOOLS
Provides efficient caching for frequently accessed data to improve performance.
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, Callable
from threading import Lock
from PyQt5.QtCore import QObject, QTimer


class CacheEntry:
    """Individual cache entry with expiration."""
    
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > self.ttl
    
    def refresh(self, new_value: Any = None, ttl: int = None):
        """Refresh cache entry with new value and/or TTL."""
        if new_value is not None:
            self.value = new_value
        if ttl is not None:
            self.ttl = ttl
        self.created_at = time.time()


class CacheManager(QObject):
    """
    Thread-safe cache manager with TTL support and automatic cleanup.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._cleanup_timer = QTimer()
        self._cleanup_timer.timeout.connect(self._cleanup_expired)
        self._cleanup_timer.start(60000)  # Cleanup every minute
        
        # Cache statistics
        self._hits = 0
        self._misses = 0
        self._sets = 0
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self._hits += 1
                    return entry.value
                else:
                    # Remove expired entry
                    del self._cache[key]
            
            self._misses += 1
            return default
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL."""
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)
            self._sets += 1
    
    def get_or_compute(self, key: str, compute_func: Callable[[], Any], ttl: int = 300) -> Any:
        """Get value from cache or compute if not exists/expired."""
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        computed_value = compute_func()
        self.set(key, computed_value, ttl)
        return computed_value
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "sets": self._sets,
                "hit_rate": round(hit_rate, 2),
                "size": len(self._cache)
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        with self._lock:
            entries_info = {}
            for key, entry in self._cache.items():
                entries_info[key] = {
                    "created_at": entry.created_at,
                    "ttl": entry.ttl,
                    "remaining_ttl": max(0, entry.ttl - (time.time() - entry.created_at)),
                    "expired": entry.is_expired()
                }
            
            return {
                "entries": entries_info,
                "stats": self.get_stats()
            }


class HardwareCache:
    """Specialized cache for hardware information."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.hardware_ttl = 3600  # Cache hardware info for 1 hour
    
    def get_gpu_info(self, compute_func: Callable[[], Dict]) -> Dict:
        """Get GPU information with caching."""
        return self.cache.get_or_compute("gpu_info", compute_func, self.hardware_ttl)
    
    def get_cpu_info(self, compute_func: Callable[[], Dict]) -> Dict:
        """Get CPU information with caching."""
        return self.cache.get_or_compute("cpu_info", compute_func, self.hardware_ttl)
    
    def get_ram_info(self, compute_func: Callable[[], Dict]) -> Dict:
        """Get RAM information with caching."""
        return self.cache.get_or_compute("ram_info", compute_func, self.hardware_ttl)
    
    def invalidate_hardware_cache(self):
        """Invalidate all hardware cache entries."""
        self.cache.delete("gpu_info")
        self.cache.delete("cpu_info")
        self.cache.delete("ram_info")


class PerformanceCache:
    """Specialized cache for performance metrics."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.performance_ttl = 5  # Cache performance metrics for 5 seconds
    
    def get_fps_estimate(self, compute_func: Callable[[], int]) -> int:
        """Get FPS estimate with caching."""
        return self.cache.get_or_compute("fps_estimate", compute_func, self.performance_ttl)
    
    def get_network_latency(self, compute_func: Callable[[], float]) -> float:
        """Get network latency with caching."""
        return self.cache.get_or_compute("network_latency", compute_func, 30)  # 30 seconds for network
    
    def cache_performance_snapshot(self, snapshot: Dict):
        """Cache a performance snapshot."""
        snapshot_key = f"perf_snapshot_{int(time.time())}"
        self.cache.set(snapshot_key, snapshot, 300)  # Keep for 5 minutes


class ConfigCache:
    """Specialized cache for configuration and settings."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.config_ttl = 1800  # Cache config for 30 minutes
    
    def get_registry_value(self, key_path: str, compute_func: Callable[[], Any]) -> Any:
        """Get registry value with caching."""
        cache_key = f"registry_{hashlib.md5(key_path.encode()).hexdigest()}"
        return self.cache.get_or_compute(cache_key, compute_func, self.config_ttl)
    
    def get_file_content(self, file_path: str, compute_func: Callable[[], str]) -> str:
        """Get file content with caching."""
        cache_key = f"file_{hashlib.md5(file_path.encode()).hexdigest()}"
        return self.cache.get_or_compute(cache_key, compute_func, self.config_ttl)
    
    def invalidate_config_cache(self):
        """Invalidate all configuration cache entries."""
        # This would require tracking all config keys, for now just clear cache
        self.cache.clear()


# Global cache instance
_global_cache = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


def initialize_caches():
    """Initialize specialized cache instances."""
    cache_manager = get_cache_manager()
    return {
        "hardware": HardwareCache(cache_manager),
        "performance": PerformanceCache(cache_manager),
        "config": ConfigCache(cache_manager)
    }
