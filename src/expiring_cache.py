class ExpiringCache:
    
    def __init__(self, default_ttl: Optional[float] = None, cleanup_interval: float = 1.0):
        """
        Initialize an expiring cache.
        
        Args:
            default_ttl: Default time-to-live in seconds for new entries.
                        If None, entries don't expire by default.
            cleanup_interval: How often to check for and remove expired entries
                            in seconds. Default is 1 second.
        """
        pass
    
    def create_cache(self, name: str) -> bool:
        """
        Create a new named cache.
        
        Args:
            name: The name of the cache to create
            
        Returns:
            True if the cache was created, False if it already exists
        """
        pass
    
    def get_cache(self, name: str) -> Optional['ExpiringCache']:
        """
        Retrieve a named cache.
        
        Args:
            name: The name of the cache to retrieve
            
        Returns:
            The ExpiringCache instance if found, otherwise None
        """
        pass
    
    def delete_cache(self, name: str) -> bool:
        """
        Delete a named cache.
        
        Args:
            name: The name of the cache to delete
            
        Returns:
            True if the cache was deleted, False if it did not exist
        """
        pass