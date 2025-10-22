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
            'INSPECT': self._handle_inspect
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
        return 'PONG'

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
        self.store.prepend(key, value)
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
        self.store.set(key, value)
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