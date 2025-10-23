"""
Cache handler module for managing multiple named caches.
Each cache is a dictionary with its own key-value pairs and expiration settings.
Supports searching, statistics, persistence, and event hooks.
"""
import time
import re
import fnmatch
import threading
from typing import Dict, Any, Optional, List, Callable, Iterator, Pattern, Union, Set
from .expiring_store import ExpiringStore
from .event_handler import EventHandler, CacheEvent, CacheEventContext
from .persistence_handler import PersistenceHandler
from .stats_handler import StatsHandler, CacheStats, StoreStats

class CacheHandler:
    """
    Manages multiple named caches, where each cache is a dictionary.
    Supports operations like creating new caches, setting/getting values within caches,
    and managing cache expiration.
    """
    
    def __init__(self, default_ttl: Optional[float] = None,
                 persistence_dir: Optional[str] = None,
                 auto_persist_interval: float = 300,
                 compress_persistence: bool = True):
        """
        Initialize a new CacheHandler instance.

        Args:
            default_ttl: Default time-to-live for cache entries in seconds
            persistence_dir: Directory to store persistent cache files
            auto_persist_interval: How often to auto-save caches (seconds)
            compress_persistence: Whether to compress persistent files
        """
        self._store = ExpiringStore(default_ttl=default_ttl)
        self._lock = threading.RLock()
        self._event_handler = EventHandler()
        self._stats_handler = StatsHandler()
        self._persistence_handler = PersistenceHandler(
            persistence_dir=persistence_dir,
            auto_persist_interval=auto_persist_interval,
            compress_persistence=compress_persistence
        )
        
        # Load any existing persistent caches
        if persistence_dir:
            self._load_persistent_caches()
        
        # Set up persistence
        if persistence_dir:
            os.makedirs(persistence_dir, exist_ok=True)
            self._load_persistent_caches()
            
            # Start auto-persist thread if interval > 0
            if auto_persist_interval > 0:
                self._stop_persist = threading.Event()
                self._persist_thread = threading.Thread(
                    target=self._auto_persist_loop,
                    args=(auto_persist_interval,),
                    daemon=True
                )
                self._persist_thread.start()
        
    def create_cache(self, cache_name: str) -> bool:
        """
        Create a new named cache.
        
        Args:
            cache_name: Name of the cache to create
            
        Returns:
            bool: True if cache was created, False if it already existed
        """
        with self._lock:
            if self._store.get(cache_name) is not None:
                return False
            self._store.set(cache_name, {})
            self._stats_handler.register_cache(cache_name)
            return True
        
    def delete_cache(self, cache_name: str) -> bool:
        """
        Delete an entire cache.
        
        Args:
            cache_name: Name of the cache to delete
            
        Returns:
            bool: True if cache was deleted, False if it didn't exist
        """
        if cache_name not in self._store:
            return False
        del self._store[cache_name]
        return True
        
    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Set a value in a specific cache.
        
        Args:
            cache_name: Name of the cache to use
            key: Key within the cache
            value: Value to store
            ttl: Optional time-to-live in seconds
            
        Returns:
            bool: True if value was set, False if cache doesn't exist
            
        Note:
            Creates the cache if it doesn't exist
        """
        with self._lock:
            cache = self._store.get(cache_name)
            if cache is None:
                cache = {}
                self._store.set(cache_name, cache, ttl)
                self._stats_handler.register_cache(cache_name)
            
            cache[key] = value
            self._stats_handler.update_cache_items(cache_name, len(cache))
            return True
        
    def get(self, cache_name: str, key: str, default: Any = None) -> Any:
        """
        Get a value from a specific cache.
        
        Args:
            cache_name: Name of the cache to use
            key: Key within the cache
            default: Value to return if key or cache doesn't exist
            
        Returns:
            The value if found, otherwise default
        """
        with self._lock:
            cache = self._store.get(cache_name)
            if cache is None:
                self._stats_handler.record_cache_miss(cache_name)
                return default
                
            if key in cache:
                self._stats_handler.record_cache_hit(cache_name)
                return cache[key]
            else:
                self._stats_handler.record_cache_miss(cache_name)
                return default
        
    def delete(self, cache_name: str, key: str) -> bool:
        """
        Delete a key from a specific cache.
        
        Args:
            cache_name: Name of the cache
            key: Key to delete within the cache
            
        Returns:
            bool: True if key was deleted, False if cache or key didn't exist
        """
        cache = self._store.get(cache_name)
        if cache is None:
            return False
        if key not in cache:
            return False
        del cache[key]
        self._stats_handler.update_cache_items(cache_name, len(cache))
        return True
        
    def list_caches(self) -> list[str]:
        """
        Get a list of all cache names.
        
        Returns:
            List of cache names
        """
        return self._store.keys()
        
    def get_cache_size(self, cache_name: str) -> int:
        """
        Get the number of items in a specific cache.
        
        Args:
            cache_name: Name of the cache
            
        Returns:
            Number of items in the cache, or 0 if cache doesn't exist
        """
        cache = self._store.get(cache_name)
        return len(cache) if cache is not None else 0
        
    def on(self, event: CacheEvent, callback: Callable[[CacheEventContext], None],
           cache_name: Optional[str] = None) -> None:
        """
        Register an event handler for cache operations.
        
        This method allows you to register callback functions that will be executed
        when specific cache events occur. Handlers can be registered globally for
        all caches or specifically for a single cache.
        
        Args:
            event: The CacheEvent type to listen for (GET, SET, DELETE, etc.)
            callback: Function to be called when the event occurs. The function
                        must accept a CacheEventContext parameter.
            cache_name: Optional name of specific cache to monitor. If None,
                        the handler will be called for events from all caches.
        
        Example:
            # Monitor all SET operations
            def on_set(ctx):
                print(f"Value set in {ctx.cache_name}: {ctx.key} = {ctx.value}")
            cache_handler.on(CacheEvent.SET, on_set)
            
            # Monitor GET operations only in "users" cache
            def on_user_access(ctx):
                print(f"User accessed: {ctx.key}")
            cache_handler.on(CacheEvent.GET, on_user_access, cache_name="users")
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        self._event_handler.on(event, callback, cache_name)
                
    def off(self, event: CacheEvent, callback: Callable[[CacheEventContext], None],
            cache_name: Optional[str] = None) -> bool:
        """
        Remove a previously registered event handler.
        
        This method allows you to unregister a callback function that was previously
        registered using the 'on' method. The event type and cache name (if any)
        must match the original registration.
        
        Args:
            event: The CacheEvent type the handler was registered for
            callback: The callback function to remove
            cache_name: Optional cache name if the handler was registered for
                       a specific cache
        
        Returns:
            bool: True if the handler was successfully removed,
                 False if the handler wasn't found
                 
        Example:
            # Remove a global handler
            cache_handler.off(CacheEvent.SET, on_set)
            
            # Remove a cache-specific handler
            cache_handler.off(CacheEvent.GET, on_user_access, cache_name="users")
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        return self._event_handler.off(event, callback, cache_name)
                
    def _trigger_event(self, event: CacheEvent, context: CacheEventContext) -> None:
        """
        Internal method to trigger event callbacks.
        
        This method is called internally when cache operations occur. It executes
        all registered handlers for the event, both cache-specific and global.
        
        Args:
            event: The CacheEvent that occurred
            context: CacheEventContext containing details about the event
            
        Note:
            - Handlers are executed synchronously in the current thread
            - Exceptions in handlers are caught and suppressed to prevent
              affecting cache operations
            - Cache-specific handlers are executed before global handlers
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        self._event_handler.trigger_event(event, context)
                    
    def clear_cache(self, cache_name: str) -> bool:
        """
        Remove all items from a specific cache.
        
        Args:
            cache_name: Name of the cache to clear
            
        Returns:
            bool: True if cache was cleared, False if it didn't exist
        """
        with self._lock:
            cache = self._store.get(cache_name)
            if cache is None:
                return False
                
            # Trigger events for each item being cleared
            for key, value in cache.items():
                self._trigger_event(CacheEvent.DELETE, CacheEventContext(
                    cache_name=cache_name,
                    key=key,
                    old_value=value,
                    event_type=CacheEvent.DELETE
                ))
                
            cache.clear()
            if cache_name in self._stats:
                self._stats[cache_name].items = 0
                
            # Trigger clear event
            self._trigger_event(CacheEvent.CLEAR, CacheEventContext(
                cache_name=cache_name,
                event_type=CacheEvent.CLEAR
            ))
            return True
            
    # Search and Filter Methods
    
    def search(self, cache_name: str, 
              predicate: Callable[[str, Any], bool]) -> Iterator[tuple[str, Any]]:
        """
        Search a cache using a predicate function.
        
        Args:
            cache_name: Name of the cache to search
            predicate: Function that takes (key, value) and returns bool
            
        Returns:
            Iterator of (key, value) pairs that match the predicate
        """
        cache = self._store.get(cache_name)
        if cache is None:
            return iter(())
            
        with self._lock:
            return ((k, v) for k, v in cache.items() if predicate(k, v))

    def search_by_pattern(self, cache_name: str, 
                         key_pattern: Optional[str] = None,
                         regex: bool = False) -> Iterator[tuple[str, Any]]:
        """
        Search using glob patterns or regex.
        
        Args:
            cache_name: Name of the cache to search
            key_pattern: Pattern to match keys against (glob or regex)
            regex: If True, treat pattern as regex, else as glob
            
        Returns:
            Iterator of matching (key, value) pairs
            
        Examples:
            # Glob pattern (default)
            search_by_pattern("users", "user_*")  # Matches user_1, user_2, etc.
            
            # Regex pattern
            search_by_pattern("users", "^user_\\d+$", regex=True)
        """
        if not key_pattern:
            return self.search(cache_name, lambda k, v: True)
            
        if regex:
            pattern = re.compile(key_pattern)
            return self.search(cache_name, lambda k, v: bool(pattern.match(k)))
        else:
            return self.search(cache_name, lambda k, v: fnmatch.fnmatch(k, key_pattern))
            
    def search_json_path(self, cache_name: str, 
                        path_pattern: str) -> Iterator[tuple[str, Any]]:
        """
        Search using a simplified JSON path pattern.
        
        Args:
            cache_name: Name of the cache to search
            path_pattern: Path pattern (e.g., "user.*.name" or "items[0].id")
            
        Returns:
            Iterator of matching (key, value) pairs
            
        Examples:
            search_json_path("users", "preferences.theme")  # Match specific path
            search_json_path("users", "*.name")  # Match any object's name
        """
        def match_path(value: Any, parts: List[str]) -> bool:
            if not parts:
                return True
            if not isinstance(value, dict):
                return False
                
            part = parts[0]
            if part == "*":
                return any(match_path(v, parts[1:]) for v in value.values())
            return part in value and match_path(value[part], parts[1:])
            
        path_parts = path_pattern.split(".")
        return self.search(cache_name, lambda k, v: match_path(v, path_parts))
            
    def find_by_value(self, cache_name: str, value_pattern: Any) -> List[str]:
        """
        Find all keys where the value matches a pattern.
        
        Args:
            cache_name: Name of the cache to search
            value_pattern: Value or dict pattern to match
            
        Returns:
            List of matching keys
        """
        def match_pattern(pattern: Any, value: Any) -> bool:
            if isinstance(pattern, dict) and isinstance(value, dict):
                return all(k in value and match_pattern(v, value[k]) 
                         for k, v in pattern.items())
            return pattern == value
            
        return [k for k, v in self.search(cache_name, 
                lambda _, v: match_pattern(value_pattern, v))]
                
    # Statistics Methods
    
    def get_stats(self, cache_name: str) -> Optional[CacheStats]:
        """Get statistics for a specific cache."""
        return self._stats_handler.get_cache_stats(cache_name)
        
    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all caches."""
        return self._stats_handler.get_all_cache_stats()
        
    def reset_stats(self, cache_name: str) -> bool:
        """Reset statistics for a specific cache."""
        return self._stats_handler.reset_cache_stats(cache_name)
        
    def get_store_stats(self) -> 'StoreStats':
        """Get statistics for the store."""
        return self._stats_handler.get_store_stats()
        
    # Persistence Methods
    
    def persist(self, cache_name: str) -> bool:
        """
        Save a cache to disk.
        
        Args:
            cache_name: Name of the cache to persist
            
        Returns:
            bool: True if successful, False otherwise
        """
        cache = self._store.get(cache_name)
        if cache is None:
            return False
            
        stats = self._stats.get(cache_name, CacheStats())
        return self._persistence_handler.persist(cache_name, cache, stats)
            
    def persist_all(self) -> int:
        """
        Save all caches to disk.
        
        Returns:
            Number of caches successfully persisted
        """
        count = 0
        for cache_name in self.list_caches():
            if self.persist(cache_name):
                count += 1
        return count
        
    def _load_persistent_caches(self) -> None:
        """Load all persistent caches during initialization."""
        for cache_name in self._persistence_handler.get_cache_files():
            self._load_cache(cache_name)
                
    def _load_cache(self, cache_name: str) -> bool:
        """
        Load a single cache from disk.
        
        Args:
            cache_name: Name of the cache to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        result = self._persistence_handler.load_persistent(cache_name)
        if result is None:
            return False
            
        cache_data, stats = result
        with self._lock:
            self._store.set(cache_name, cache_data)
            self._stats_handler.register_cache(cache_name)
            self._stats_handler.import_cache_stats(cache_name, stats)
            
            # Trigger event
            self._trigger_event(CacheEvent.CREATE_CACHE, CacheEventContext(
                cache_name=cache_name,
                event_type=CacheEvent.CREATE_CACHE
            ))
        return True
            
    def stop(self) -> None:
        """Stop background threads and persist caches."""
        self.persist_all()  # Final persistence
        self._persistence_handler.stop()  # Stop persistence handler
        self._store.stop()  # Stop the expiring store