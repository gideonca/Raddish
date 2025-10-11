"""
Command handler for the Reddish server.
Handles execution of Redis-like commands.
"""
from typing import List, Optional, Any
from .expiring_store import ExpiringStore
from .validator import validate_command

class CommandHandler:
    def __init__(self, store: ExpiringStore):
        self.store = store

    def handle_command(self, command_parts: List[str], send_response) -> bool:
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

        command = command_parts[0].upper()
        
        # Handle EXIT command to close connection
        if command == 'EXIT':
            send_response(b'Goodbye!\n')
            return False
            
        # Validate command
        is_valid, error_msg = validate_command(command_parts)
        if not is_valid:
            send_response(f'ERROR: {error_msg}\n'.encode('utf-8'))
            return True

        # Handle command
        try:
            response = self._execute_command(command, command_parts[1:])
            send_response(f'{response}\n'.encode('utf-8'))
        except Exception as e:
            send_response(f'ERROR: {str(e)}\n'.encode('utf-8'))
            
        return True

    def _execute_command(self, command: str, args: List[str]) -> str:
        """Execute a command and return the response string."""
        match command:
            case 'PING':
                return 'PONG'
                
            case 'ECHO':
                return ' '.join(args)
                
            case 'SET':
                key, value = args[0], args[1]
                self.store.set(key, value)
                return 'OK'
                
            case 'GET':
                key = args[0]
                value = self.store.get(key, 'NULL')
                return str(value)
                
            case 'DEL' | 'LPOP':
                key = args[0]
                if key in self.store:
                    del self.store[key]
                    return 'OK'
                return 'NULL'
                
            case 'EXPIRE':
                key, ttl = args[0], int(args[1])
                if key in self.store:
                    value = self.store.get(key)
                    self.store.set(key, value, ttl=ttl)
                    return 'OK'
                return 'NULL'
                
            case 'LPUSH':
                key, value = args[0], args[1]
                self.store.prepend(key, value)
                return 'OK'
                
            case 'RPUSH':
                key, value = args[0], args[1]
                self.store.set(key, value)
                return 'OK'
                
            case 'INSPECT':
                result = []
                for k in self.store.keys():
                    v = self.store.get(k)
                    result.append(f'{k}: {v}')
                result.append('END')
                return '\n'.join(result)
                
            case _:
                raise ValueError(f'Unknown command: {command}')
