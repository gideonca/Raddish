"""
Event handler for the Reddish server.

This module handles event-related functionality like sending responses,
managing client connections, and cache events. It separates event handling
from command and cache processing logic.
"""
import time
import threading
from enum import Enum
from typing import Callable, Dict, Set, Any, Optional
from dataclasses import dataclass

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


class EventHandler:
    """
    Handles event-related functionality for the Redis-like server.
    
    This class provides a clean interface for managing events and responses,
    separating these concerns from command and cache processing logic.
    """

    def __init__(self):
        """Initialize the event handler."""
        self._lock = threading.RLock()
        
        # Event handlers: (cache_name, event_type) -> set of callbacks
        self._event_handlers: Dict[tuple[str, CacheEvent], Set[Callable]] = {}
        # Global handlers: event_type -> set of callbacks
        self._global_handlers: Dict[CacheEvent, Set[Callable]] = {}

    def handle_response(self, response: str, send_response: Callable) -> None:
        """
        Handle sending a response to the client.
        
        Args:
            response: The response string to send
            send_response: Callback function to send response to client
        """
        send_response(f'{response}\n'.encode('utf-8'))

    def handle_error(self, error_msg: str, send_response: Callable) -> None:
        """
        Handle sending an error response to the client.
        
        Args:
            error_msg: The error message to send
            send_response: Callback function to send response to client
        """
        send_response(f'ERROR: {error_msg}\n'.encode('utf-8'))

    def handle_exit(self, send_response: Callable) -> bool:
        """
        Handle client exit request.
        
        Args:
            send_response: Callback function to send response to client
            
        Returns:
            bool: False to indicate connection should be closed
        """
        send_response(b'Goodbye!\n')
        return False

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
            
        Thread Safety:
            This method is thread-safe and can be called concurrently.
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
        Remove a previously registered event handler.
        
        Args:
            event: The CacheEvent type the handler was registered for
            callback: The callback function to remove
            cache_name: Optional cache name if the handler was registered for
                       a specific cache
        
        Returns:
            bool: True if the handler was successfully removed,
                 False if the handler wasn't found
                 
        Thread Safety:
            This method is thread-safe and can be called concurrently.
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
                
    def trigger_event(self, event: CacheEvent, context: CacheEventContext) -> None:
        """
        Trigger event callbacks.
        
        This method is called when cache operations occur. It executes
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