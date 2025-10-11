from typing import Any, Optional, Dict, List, Tuple
import time
import threading

class ExpiringStore:
    """
    A thread-safe key-value store with automatic key expiration.
    
    This class implements a dictionary-like object where entries can automatically
    expire after a specified time-to-live (TTL). A background thread periodically
    removes expired entries. All operations are thread-safe.
    
    Attributes:
        default_ttl (float): Default time-to-live in seconds for new entries
        cleanup_interval (float): How often the cleanup thread runs in seconds
    """
    
    def __init__(self, default_ttl: Optional[float] = None, cleanup_interval: float = 1.0):
        """
        Initialize an expiring store.
        
        Args:
            default_ttl: Default time-to-live in seconds for new entries.
                        If None, entries don't expire by default.
            cleanup_interval: How often to check for and remove expired entries
                            in seconds. Default is 1 second.
        """
        self._store: Dict[Any, Tuple[Any, Optional[float]]] = {}
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Start the cleanup thread
        self._thread = threading.Thread(
            target=self._auto_cleanup,
            daemon=True,
            name="ExpiringStore-Cleanup"
        )
        self._thread.start()
        
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set a key-value pair with optional TTL.
        
        Args:
            key: The key to set
            value: The value to store
            ttl: Time-to-live in seconds. If None, uses the default_ttl.
                 If both are None, the entry never expires.
                 
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        expiry = None
        ttl = ttl if ttl is not None else self.default_ttl
        if ttl is not None:
            expiry = time.time() + ttl
        with self._lock:
            self._store[key] = (value, expiry)
            
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get a value by key, returning default if missing or expired.
        
        Args:
            key: The key to look up
            default: Value to return if key is missing or expired
            
        Returns:
            The value if present and not expired, otherwise the default value.
            
        Note:
            This method will remove the key if it's expired when accessed.
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return default
            value, expiry = item
            if expiry is None or expiry > time.time():
                return value
            else:
                # expired - remove and return default
                del self._store[key]
                return default
            
    def prepend(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        """
        Insert a key-value pair at the beginning of the store.
        
        This maintains insertion order by recreating the store with the new
        item at the front. Useful for implementing LPUSH-like operations.
        
        Args:
            key: The key to prepend
            value: The value to store
            ttl: Optional time-to-live in seconds
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        expiry = None
        if ttl is not None:
            expiry = time.time() + ttl
        with self._lock:
            self._store = {key: (value, expiry), **self._store}
            
    def keys(self) -> List[Any]:
        """
        Get a list of all non-expired keys in the store.
        
        This method triggers a cleanup of expired keys before returning
        the list of current keys.
        
        Returns:
            List of all non-expired keys in the store.
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        self.cleanup()  # Remove any expired keys first
        return list(self._store.keys())
            
    def __contains__(self, key: Any) -> bool:
        """
        Check if a key exists and is not expired.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists and is not expired, False otherwise.
        """
        return self.get(key) is not None

    def __delitem__(self, key: Any) -> None:
        """
        Delete a key from the store.
        
        Args:
            key: The key to delete
            
        Raises:
            KeyError: If the key doesn't exist
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        with self._lock:
            if key in self._store:
                del self._store[key]
            else:
                raise KeyError(key)
    
    def cleanup(self) -> None:
        """
        Remove all expired entries from the store.
        
        This is called periodically by the background thread and can also
        be called manually if needed.
        
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        now = time.time()
        with self._lock:
            expired = [k for k, (_, expiry) in self._store.items()
                      if expiry and expiry <= now]
            for k in expired:
                del self._store[k]
                
    def _auto_cleanup(self) -> None:
        """
        Background thread that periodically calls cleanup().
        
        This method runs in a separate thread and continues until stop()
        is called or the program exits.
        """
        while not self._stop_event.is_set():
            self.cleanup()
            time.sleep(self.cleanup_interval)
            
    def stop(self) -> None:
        """
        Stop the background cleanup thread.
        
        This should be called before program exit to ensure clean shutdown.
        It's safe to call this method multiple times.
        """
        self._stop_event.set()
        self._thread.join()
        
    def __repr__(self) -> str:
        """
        Get a string representation of the store.
        
        Returns:
            A string showing the class name and current store contents.
        """
        return f"ExpiringStore({self._store})"
    
    def clear(self) -> None:
        """
        Remove all items from the store.
        
        This removes all items regardless of their expiration time.
        
        Thread Safety:
            This method is thread-safe and can be called concurrently.
        """
        with self._lock:
            self._store.clear()