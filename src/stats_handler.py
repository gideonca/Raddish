"""
Statistics handler module for tracking cache and store metrics.

This module manages statistics tracking for caches and stores,
providing a centralized way to track and analyze usage patterns.
"""
import time
from typing import Dict, Optional
from dataclasses import dataclass, field

@dataclass
class CacheStats:
    """Statistics for a single cache"""
    hits: int = 0
    misses: int = 0
    items: int = 0
    last_access: float = 0
    last_write: float = 0
    created_at: float = field(default_factory=time.time)

@dataclass
class StoreStats:
    """Statistics for an expiring store"""
    total_items: int = 0
    expired_items: int = 0
    total_hits: int = 0
    total_misses: int = 0
    last_cleanup: float = 0
    created_at: float = field(default_factory=time.time)

class StatsHandler:
    """
    Handles statistics tracking for caches and stores.
    
    This class provides a centralized way to track and manage statistics
    for both individual caches and the overall store.
    """
    
    def __init__(self):
        """Initialize the statistics handler."""
        self._cache_stats: Dict[str, CacheStats] = {}
        self._store_stats = StoreStats()

    def register_cache(self, cache_name: str) -> None:
        """
        Register a new cache for statistics tracking.
        
        Args:
            cache_name: Name of the cache to register
        """
        if cache_name not in self._cache_stats:
            self._cache_stats[cache_name] = CacheStats()

    def unregister_cache(self, cache_name: str) -> None:
        """
        Remove a cache from statistics tracking.
        
        Args:
            cache_name: Name of the cache to unregister
        """
        self._cache_stats.pop(cache_name, None)

    def record_cache_hit(self, cache_name: str) -> None:
        """
        Record a cache hit for the specified cache.
        
        Args:
            cache_name: Name of the cache
        """
        if cache_name in self._cache_stats:
            stats = self._cache_stats[cache_name]
            stats.hits += 1
            stats.last_access = time.time()
            self._store_stats.total_hits += 1

    def record_cache_miss(self, cache_name: str) -> None:
        """
        Record a cache miss for the specified cache.
        
        Args:
            cache_name: Name of the cache
        """
        if cache_name in self._cache_stats:
            stats = self._cache_stats[cache_name]
            stats.misses += 1
            stats.last_access = time.time()
            self._store_stats.total_misses += 1

    def update_cache_items(self, cache_name: str, item_count: int) -> None:
        """
        Update the item count for a cache.
        
        Args:
            cache_name: Name of the cache
            item_count: New number of items in the cache
        """
        if cache_name in self._cache_stats:
            stats = self._cache_stats[cache_name]
            stats.items = item_count
            stats.last_write = time.time()

    def record_item_expired(self) -> None:
        """Record that an item has expired in the store."""
        self._store_stats.expired_items += 1

    def record_cleanup(self) -> None:
        """Record that a cleanup operation was performed."""
        self._store_stats.last_cleanup = time.time()

    def update_total_items(self, count: int) -> None:
        """
        Update the total number of items in the store.
        
        Args:
            count: New total item count
        """
        self._store_stats.total_items = count

    def get_cache_stats(self, cache_name: str) -> Optional[CacheStats]:
        """
        Get statistics for a specific cache.
        
        Args:
            cache_name: Name of the cache
            
        Returns:
            CacheStats if the cache exists, None otherwise
        """
        return self._cache_stats.get(cache_name)

    def get_all_cache_stats(self) -> Dict[str, CacheStats]:
        """
        Get statistics for all caches.
        
        Returns:
            Dictionary mapping cache names to their statistics
        """
        return dict(self._cache_stats)

    def get_store_stats(self) -> StoreStats:
        """
        Get statistics for the store.
        
        Returns:
            StoreStats object with current store statistics
        """
        return self._store_stats

    def reset_cache_stats(self, cache_name: str) -> bool:
        """
        Reset statistics for a specific cache.
        
        Args:
            cache_name: Name of the cache
            
        Returns:
            bool: True if stats were reset, False if cache doesn't exist
        """
        if cache_name in self._cache_stats:
            self._cache_stats[cache_name] = CacheStats()
            return True
        return False

    def reset_store_stats(self) -> None:
        """Reset all store statistics."""
        self._store_stats = StoreStats()

    def import_cache_stats(self, cache_name: str, stats: CacheStats) -> None:
        """
        Import statistics for a cache (used when loading from persistence).
        
        Args:
            cache_name: Name of the cache
            stats: Statistics to import
        """
        self._cache_stats[cache_name] = stats