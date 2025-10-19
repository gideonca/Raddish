"""
Cache handler module for managing multiple named caches.
Each cache is a dictionary with its own key-value pairs and expiration settings.
Supports searching, statistics, persistence, and event hooks.
"""
import json
import time
import os
import re
import gzip
import fnmatch
import threading
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Iterator, Pattern, Set, Union
from dataclasses import dataclass
from .expiring_store import ExpiringStore

class CacheEvent(Enum):
    """Events that can trigger callbacks"""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    EXPIRE = "expire"
    CLEAR = "clear"
    CREATE_CACHE = "create_cache"
    DELETE_CACHE = "delete_cache"

@dataclass
class CacheEventContext:
    """Context information for cache events"""
    cache_name: str
    key: Optional[str]
    value: Any = None
    old_value: Any = None
    event_type: CacheEvent = CacheEvent.GET
    timestamp: float = time.time()

@dataclass
class CacheStats:
    """Statistics for a single cache"""
    hits: int = 0
    misses: int = 0
    items: int = 0
    last_access: float = 0
    last_write: float = 0
    created_at: float = time.time()

class CacheHandler:
    """
    Manages multiple named caches, where each cache is a dictionary.
    Supports operations like creating new caches, setting/getting values within caches,
    and managing cache expiration.
    """
    
    def __init__(self, default_ttl: Optional[float] = None, 
                 persistence_dir: Optional[str] = None,
                 auto_persist_interval: float = 300,  # 5 minutes
                 compress_persistence: bool = True):
        """
        Initialize the cache handler.
        
        Args:
            default_ttl: Default time-to-live for cache entries in seconds
            persistence_dir: Directory to store persistent cache files
            auto_persist_interval: How often to auto-save caches (seconds)
            compress_persistence: Whether to compress persistent files
        """
        self._store = ExpiringStore(default_ttl=default_ttl)
        self._stats = {}  # Cache name -> CacheStats
        self._persistence_dir = persistence_dir
        self._compress_persistence = compress_persistence
        self._lock = threading.RLock()
        
        # Event handlers: (cache_name, event_type) -> set of callbacks
        self._event_handlers: Dict[tuple[str, CacheEvent], Set[Callable]] = {}
        # Global handlers: event_type -> set of callbacks
        self._global_handlers: Dict[CacheEvent, Set[Callable]] = {}
        
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
            self._stats[cache_name] = CacheStats()
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
                self._stats[cache_name] = CacheStats()
            
            cache[key] = value
            stats = self._stats[cache_name]
            stats.items = len(cache)
            stats.last_write = time.time()
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
                if cache_name in self._stats:
                    self._stats[cache_name].misses += 1
                return default
                
            stats = self._stats[cache_name]
            stats.last_access = time.time()
            
            if key in cache:
                stats.hits += 1
                return cache[key]
            else:
                stats.misses += 1
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
        Register an event handler.
        
        Args:
            event: Event type to listen for
            callback: Function to call when event occurs
            cache_name: Optional cache name to filter events
            
        Example:
            def on_set(ctx):
                print(f"Value set in {ctx.cache_name}: {ctx.key} = {ctx.value}")
            
            cache_handler.on(CacheEvent.SET, on_set)
        """
        with self._lock:
            if cache_name:
                key = (cache_name, event)
                if key not in self._event_handlers:
                    self._event_handlers[key] = set()
                self._event_handlers[key].add(callback)
            else:
                if event not in self._global_handlers:
                    self._global_handlers[event] = set()
                self._global_handlers[event].add(callback)
                
    def off(self, event: CacheEvent, callback: Callable[[CacheEventContext], None],
            cache_name: Optional[str] = None) -> bool:
        """
        Remove an event handler.
        
        Returns:
            bool: True if handler was removed, False if not found
        """
        with self._lock:
            try:
                if cache_name:
                    self._event_handlers[(cache_name, event)].remove(callback)
                else:
                    self._global_handlers[event].remove(callback)
                return True
            except KeyError:
                return False
                
    def _trigger_event(self, event: CacheEvent, context: CacheEventContext) -> None:
        """Trigger event callbacks."""
        with self._lock:
            # Call cache-specific handlers
            if context.cache_name:
                handlers = self._event_handlers.get((context.cache_name, event), set())
                for handler in handlers:
                    try:
                        handler(context)
                    except Exception:
                        pass  # Don't let handler errors propagate
                        
            # Call global handlers
            handlers = self._global_handlers.get(event, set())
            for handler in handlers:
                try:
                    handler(context)
                except Exception:
                    pass
                    
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
        return self._stats.get(cache_name)
        
    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all caches."""
        return dict(self._stats)
        
    def reset_stats(self, cache_name: str) -> bool:
        """Reset statistics for a specific cache."""
        if cache_name in self._stats:
            self._stats[cache_name] = CacheStats()
            return True
        return False
        
    # Persistence Methods
    
    def persist(self, cache_name: str) -> bool:
        """
        Save a cache to disk, optionally compressed.
        
        Args:
            cache_name: Name of the cache to persist
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._persistence_dir:
            return False
            
        cache = self._store.get(cache_name)
        if cache is None:
            return False
            
        try:
            data = json.dumps({
                'data': cache,
                'stats': vars(self._stats.get(cache_name, CacheStats()))
            }).encode('utf-8')
            
            if self._compress_persistence:
                path = os.path.join(self._persistence_dir, f"{cache_name}.json.gz")
                with gzip.open(path, 'wb') as f:
                    f.write(data)
            else:
                path = os.path.join(self._persistence_dir, f"{cache_name}.json")
                with open(path, 'wb') as f:
                    f.write(data)
                    
            return True
        except Exception:
            return False
            
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
        
    def load_persistent(self, cache_name: str) -> bool:
        """
        Load a cache from disk, handling both compressed and uncompressed files.
        
        Args:
            cache_name: Name of the cache to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._persistence_dir:
            return False
            
        # Try compressed file first
        gz_path = os.path.join(self._persistence_dir, f"{cache_name}.json.gz")
        json_path = os.path.join(self._persistence_dir, f"{cache_name}.json")
        
        try:
            if os.path.exists(gz_path):
                with gzip.open(gz_path, 'rb') as f:
                    data = json.loads(f.read().decode('utf-8'))
            elif os.path.exists(json_path):
                with open(json_path, 'rb') as f:
                    data = json.loads(f.read().decode('utf-8'))
            else:
                return False
                
            with self._lock:
                self._store.set(cache_name, data['data'])
                self._stats[cache_name] = CacheStats(**data['stats'])
                
                # Trigger event
                self._trigger_event(CacheEvent.CREATE_CACHE, CacheEventContext(
                    cache_name=cache_name,
                    event_type=CacheEvent.CREATE_CACHE
                ))
            return True
        except Exception:
            return False
            
    def _load_persistent_caches(self) -> None:
        """Load all persistent caches during initialization."""
        if not self._persistence_dir:
            return
            
        for filename in os.listdir(self._persistence_dir):
            if filename.endswith('.json'):
                cache_name = filename[:-5]  # Remove .json
                self.load_persistent(cache_name)
                
    def _auto_persist_loop(self, interval: float) -> None:
        """Background thread for automatic persistence."""
        while not getattr(self, '_stop_persist', threading.Event()).is_set():
            self.persist_all()
            time.sleep(interval)
            
    def stop(self) -> None:
        """Stop background threads and persist caches."""
        if hasattr(self, '_stop_persist'):
            self._stop_persist.set()
            if hasattr(self, '_persist_thread'):
                self._persist_thread.join()
        self.persist_all()  # Final persistence
        self._store.stop()  # Stop the expiring store