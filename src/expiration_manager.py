import time
import threading

class ExpiringDict():
    def __init__(self, default_ttl: float = None, cleanup_interval: float = 1.0):
        self._store = {}
        self.default_ttl = default_ttl # Time-to-live in seconds
        self.cleanup_interval = cleanup_interval
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Start the cleanup thread
        self._thread = threading.Thread(target= self._auto_cleanup, daemon=True)
        self._thread.start()
        
    def set(self, key, value, ttl: float = None):
        expiry = None
        ttl = ttl if ttl is not None else self.default_ttl
        if ttl is not None:
            expiry = time.time() + ttl
        with self._lock:
            self._store[key] = (value, expiry)
            
    def get(self, key, default=None):
        with self._lock:
            item = self._store.get(key)
            # If key is missing, return default
            if item is None:
                return default
            # Unpack stored tuple (value, expiry)
            value, expiry = item
            if expiry is None or expiry > time.time():
                return value
            else:
                # expired
                del self._store[key]
                return default
            
    def __contains__(self, key):
        return self.get(key) is not None
    
    def cleanup(self):
        """Remove expired items from the store."""
        now = time.time()
        with self._lock:
            expired = [k for k, (_, expiry) in self._store.items() if expiry and expiry <= now]
            for k in expired:
                del self._store[k]
                
    def _auto_cleanup(self):
        """Background loop cleanup"""
        while not self._stop_event.is_set():
            self.cleanup()
            time.sleep(self.cleanup_interval)
            
    def stop(self):
        """Stop the background cleanup thread."""
        self._stop_event.set()
        self._thread.join() 
        
    def __repr__(self):
        return f"ExpiringDict({self._store})"