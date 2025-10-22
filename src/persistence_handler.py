"""
Persistence handler module for managing cache persistence.

This module handles saving and loading cache data to/from disk,
with support for compression and automatic persistence.
"""
import os
import json
import gzip
import time
import threading
from typing import Any, Optional, Dict
from dataclasses import dataclass
from .expiring_store import ExpiringStore

@dataclass
class CacheStats:
    """Statistics for a single cache"""
    hits: int = 0
    misses: int = 0
    items: int = 0
    last_access: float = 0
    last_write: float = 0
    created_at: float = time.time()

class PersistenceHandler:
    """
    Handles persistence operations for cache data.
    
    This class manages saving and loading cache data to/from disk,
    with support for both compressed and uncompressed storage.
    """
    
    def __init__(self, persistence_dir: Optional[str] = None,
                 auto_persist_interval: float = 300,  # 5 minutes
                 compress_persistence: bool = True):
        """
        Initialize the persistence handler.
        
        Args:
            persistence_dir: Directory to store persistent cache files
            auto_persist_interval: How often to auto-save caches (seconds)
            compress_persistence: Whether to compress persistent files
        """
        self._persistence_dir = persistence_dir
        self._compress_persistence = compress_persistence
        self._lock = threading.RLock()
        
        # Set up persistence
        if persistence_dir:
            os.makedirs(persistence_dir, exist_ok=True)
            
            # Start auto-persist thread if interval > 0
            if auto_persist_interval > 0:
                self._stop_persist = threading.Event()
                self._persist_thread = threading.Thread(
                    target=self._auto_persist_loop,
                    args=(auto_persist_interval,),
                    daemon=True
                )
                self._persist_thread.start()

    def persist(self, cache_name: str, cache_data: dict, stats: CacheStats) -> bool:
        """
        Save a cache to disk, optionally compressed.
        
        Args:
            cache_name: Name of the cache to persist
            cache_data: The cache data to persist
            stats: The cache statistics to persist
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._persistence_dir:
            return False
            
        try:
            data = json.dumps({
                'data': cache_data,
                'stats': vars(stats)
            }).encode('utf-8')
            
            with self._lock:
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

    def load_persistent(self, cache_name: str) -> Optional[tuple[dict, CacheStats]]:
        """
        Load a cache from disk, handling both compressed and uncompressed files.
        
        Args:
            cache_name: Name of the cache to load
            
        Returns:
            Optional tuple of (cache_data, cache_stats) if successful,
            None if the cache couldn't be loaded
        """
        if not self._persistence_dir:
            return None
            
        # Try compressed file first
        gz_path = os.path.join(self._persistence_dir, f"{cache_name}.json.gz")
        json_path = os.path.join(self._persistence_dir, f"{cache_name}.json")
        
        try:
            with self._lock:
                if os.path.exists(gz_path):
                    with gzip.open(gz_path, 'rb') as f:
                        data = json.loads(f.read().decode('utf-8'))
                elif os.path.exists(json_path):
                    with open(json_path, 'rb') as f:
                        data = json.loads(f.read().decode('utf-8'))
                else:
                    return None
                
            return data['data'], CacheStats(**data['stats'])
        except Exception:
            return None

    def get_cache_files(self) -> list[str]:
        """
        Get a list of all persisted cache files.
        
        Returns:
            List of cache names (without file extensions)
        """
        if not self._persistence_dir:
            return []
            
        cache_files = []
        for filename in os.listdir(self._persistence_dir):
            if filename.endswith('.json.gz'):
                cache_files.append(filename[:-8])  # Remove .json.gz
            elif filename.endswith('.json'):
                cache_files.append(filename[:-5])  # Remove .json
        return cache_files

    def _auto_persist_loop(self, interval: float) -> None:
        """Background thread for automatic persistence."""
        while not getattr(self, '_stop_persist', threading.Event()).is_set():
            time.sleep(interval)

    def stop(self) -> None:
        """Stop background threads."""
        if hasattr(self, '_stop_persist'):
            self._stop_persist.set()
            if hasattr(self, '_persist_thread'):
                self._persist_thread.join()