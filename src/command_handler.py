"""
Command handler for the Reddish server.

This module implements a Redis-like command handler using the command pattern.
It processes incoming commands and manages interactions with the data store.
"""
from typing import List, Optional, Any, Callable, Dict, Tuple
from .expiring_store import ExpiringStore
from .validation_handler import ValidationHandler
from .event_handler import EventHandler

class CommandHandler:
    """
    Handles execution of Redis-like commands using a command dispatcher pattern.
    
    This class provides a clean interface for executing Redis-style commands
    against a data store. It uses a dispatcher pattern for efficient command 
    routing and consistent error handling.
    
    Attributes:
        store (ExpiringStore): The backing store for data persistence
        _handlers (Dict): Mapping of commands to their handler methods
        event_handler (EventHandler): Handler for event-related functionality
        validation_handler (ValidationHandler): Handler for command validation
    """

    def __init__(self, store: ExpiringStore):
        """
        Initialize a new CommandHandler instance.

        Args:
            store (ExpiringStore): The data store to use for operations
        """
        self.event_handler = EventHandler()
        self.validation_handler = ValidationHandler()
        self.store = store
        self._handlers = {
            'PING': self._handle_ping,
            'ECHO': self._handle_echo,
            'SET': self._handle_set,
            'GET': self._handle_get,
            'DEL': self._handle_del,
            'LPOP': self._handle_del,  # LPOP uses same handler as DEL
            'EXPIRE': self._handle_expire,
            'LPUSH': self._handle_lpush,
            'RPUSH': self._handle_rpush,
            'INSPECT': self._handle_inspect,
            'CREATECACHE': self._handle_create_cache,
            'DELETECACHE': self._handle_delete_cache,
            'LISTCACHES': self._handle_list_caches,
            'CREATESTORE': self._handle_create_store,
            'DELETESTORE': self._handle_delete_store,
            'LISTSTORES': self._handle_list_stores
        }

    def _preprocess_set_command(self, command_parts: List[str]) -> List[str]:
        """
        Preprocess SET command to handle JSON values with spaces.
        
        Args:
            command_parts: Original command parts
            
        Returns:
            List[str]: Processed command parts with JSON value combined
        """
        if len(command_parts) < 3:
            return command_parts
            
        # If this is a SET command with more parts than expected,
        # combine all parts after the key into a single value
        if command_parts[0].upper() == 'SET' and len(command_parts) > 3:
            return [
                command_parts[0],
                command_parts[1],
                ' '.join(command_parts[2:])
            ]
        return command_parts

    def handle_command(self, command_parts: List[str], send_response: Callable) -> bool:
        """
        Handle a command and send response through the callback.
        
        Args:
            command_parts: List of command parts (command and arguments)
            send_response: Callback function to send response to client
            
        Returns:
            bool: True if connection should stay open, False to close
        """
        if not command_parts:
            return True

        # TODO: Need to implement command logging here

        # Preprocess command parts to handle JSON values with spaces
        command_parts = self._preprocess_set_command(command_parts)
        command = command_parts[0].upper()
        
        if command == 'EXIT':
            return self.event_handler.handle_exit(send_response)
            
        is_valid, error_msg = self.validation_handler.validate_command(command_parts)
        if not is_valid:
            self.event_handler.handle_error(error_msg, send_response)
            return True

        try:
            handler = self._handlers.get(command)
            if not handler:
                raise ValueError(f'Unknown command: {command}')
                
            response = handler(command_parts[1:])
            self.event_handler.handle_response(response, send_response)
        except Exception as e:
            self.event_handler.handle_error(str(e), send_response)
            
        return True

    def _handle_ping(self, args: List[str]) -> str:
        """Handle PING command."""
        return r"""
                     .-.
                    (o o)  
                    | O \
                    \   \
                    `~~~'
                    /     \
                   /       \
                  /         \
                 /           \
                /             \
               /               \
               -----------------
                    I LIVE
                """

    def _handle_echo(self, args: List[str]) -> str:
        """
        Handle ECHO command.
        
        Args:
            args: List of arguments to echo back
            
        Returns:
            str: The joined arguments as a single string
        """
        return ' '.join(args)

    def _handle_set(self, args: List[str]) -> str:
        """
        Handle SET command.
        
        Args:
            args: [key, value] to store
            
        Returns:
            str: 'OK' on success
        """
        key, value = args[0], args[1]
        self.store.set(key, value)
        return 'OK'

    def _handle_get(self, args: List[str]) -> str:
        """
        Handle GET command.
        
        Args:
            args: [key] to retrieve
            
        Returns:
            str: The value or 'NULL' if not found
        """
        key = args[0]
        return str(self.store.get(key, 'NULL'))

    def _handle_del(self, args: List[str]) -> str:
        """
        Handle DEL/LPOP command.
        
        Args:
            args: [key] to delete
            
        Returns:
            str: 'OK' if deleted, 'NULL' if key didn't exist
        """
        key = args[0]
        if key in self.store:
            del self.store[key]
            return 'OK'
        return 'NULL'

    def _handle_expire(self, args: List[str]) -> str:
        """
        Handle EXPIRE command.
        
        Args:
            args: [key, ttl] where ttl is in seconds
            
        Returns:
            str: 'OK' if expiry set, 'NULL' if key didn't exist
        """
        key, ttl = args[0], int(args[1])
        if key in self.store:
            value = self.store.get(key)
            self.store.set(key, value, ttl=ttl)
            return 'OK'
        return 'NULL'

    def _handle_lpush(self, args: List[str]) -> str:
        """
        Handle LPUSH command.
        
        Args:
            args: [key, value] to prepend
            
        Returns:
            str: 'OK' on success
        """
        key, value = args[0], args[1]
        current = self.store.get(key, [])
        print(current)
        if not isinstance(current, list):
            current = [current] if current != 'NULL' else []
        current.insert(0, value)  # Insert at the beginning of the list
        self.store.set(key, current)
        return 'OK'

    def _handle_rpush(self, args: List[str]) -> str:
        """
        Handle RPUSH command.
        
        Args:
            args: [key, value] to append
            
        Returns:
            str: 'OK' on success
        """
        key, value = args[0], args[1]
        current = self.store.get(key, [])
        if not isinstance(current, list):
            current = [current] if current != 'NULL' else []
        current.append(value)
        self.store.set(key, current)
        return 'OK'

    def _handle_inspect(self, args: List[str]) -> str:
        """
        Handle INSPECT command.
        
        Returns:
            str: Formatted string of all key-value pairs
        """
        result = []
        for k in self.store.keys():
            v = self.store.get(k)
            result.append(f'{k}: {v}')
        result.append('END')
        return '\n'.join(result)

    def _handle_create_cache(self, args: List[str]) -> str:
        """
        Handle CREATECACHE command.
        
        Args:
            args: [cache_name] name of the cache to create
            
        Returns:
            str: 'OK' if cache was created, error message if it already exists
        """
        cache_name = args[0]
        if self.store.create_cache(cache_name):
            return 'OK'
        return f'Cache {cache_name} already exists'

    def _handle_delete_cache(self, args: List[str]) -> str:
        """
        Handle DELETECACHE command.
        
        Args:
            args: [cache_name] name of the cache to delete
            
        Returns:
            str: 'OK' if cache was deleted, error message if it didn't exist
        """
        cache_name = args[0]
        if self.store.delete_cache(cache_name):
            return 'OK'
        return f'Cache {cache_name} does not exist'

    def _handle_list_caches(self, args: List[str]) -> str:
        """
        Handle LISTCACHES command.
        
        Returns:
            str: Formatted string listing all cache names
        """
        caches = self.store.list_caches()
        if not caches:
            return 'No caches exist'
        result = ['Available caches:']
        for cache in caches:
            size = self.store.get_cache_size(cache)
            result.append(f'- {cache} ({size} items)')
        return '\n'.join(result)

    def _handle_create_store(self, args: List[str]) -> str:
        """
        Handle CREATESTORE command.
        
        Args:
            args: [cache_name, store_name, ttl?] where ttl is optional in seconds
            
        Returns:
            str: 'OK' if store was created, error message otherwise
        """
        cache_name, store_name = args[0], args[1]
        ttl = float(args[2]) if len(args) > 2 else None
        
        try:
            store = ExpiringStore(default_ttl=ttl)
            if self.store.set(cache_name, {store_name: store}):
                return 'OK'
            return f'Failed to create store {store_name} in cache {cache_name}'
        except Exception as e:
            return f'Error creating store: {str(e)}'

    def _handle_delete_store(self, args: List[str]) -> str:
        """
        Handle DELETESTORE command.
        
        Args:
            args: [cache_name, store_name]
            
        Returns:
            str: 'OK' if store was deleted, error message if it didn't exist
        """
        cache_name, store_name = args[0], args[1]
        cache = self.store.get(cache_name)
        
        if not cache:
            return f'Cache {cache_name} does not exist'
            
        if store_name not in cache:
            return f'Store {store_name} does not exist in cache {cache_name}'
            
        store = cache[store_name]
        if isinstance(store, ExpiringStore):
            store.stop()  # Stop the cleanup thread
            
        del cache[store_name]
        return 'OK'

    def _handle_list_stores(self, args: List[str]) -> str:
        """
        Handle LISTSTORES command.
        
        Args:
            args: [cache_name]
            
        Returns:
            str: Formatted string listing all stores in the cache
        """
        cache_name = args[0]
        cache = self.store.get(cache_name)
        
        if not cache:
            return f'Cache {cache_name} does not exist'
            
        stores = [name for name, value in cache.items() 
                 if isinstance(value, ExpiringStore)]
        
        if not stores:
            return f'No stores in cache {cache_name}'
            
        result = [f'Stores in cache {cache_name}:']
        for store_name in stores:
            store = cache[store_name]
            num_items = len(store.keys())
            ttl = store.default_ttl or 'No'
            result.append(f'- {store_name} ({num_items} items, {ttl} TTL)')
        return '\n'.join(result)