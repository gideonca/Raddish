"""
Command validation handler for the Raddish server.

This module provides a comprehensive validation system for Redis-like commands
through a registry-based handler pattern.
"""
from typing import Dict, Any, List, Optional, Tuple, Type

class ValidationHandler:
    """
    Handles validation of Redis-like commands through a registry-based system.
    
    This class provides a robust interface for command validation, including
    argument count validation, type checking, and usage information.
    """
    
    def __init__(self):
        """Initialize the validation handler with default command specifications."""
        # Default command specifications
        self._command_specs: Dict[str, Dict[str, Any]] = {
            'PING':    {'min_args': 1, 'max_args': 1, 'usage': 'PING'},
            'EXIT':    {'min_args': 1, 'max_args': 1, 'usage': 'EXIT'},
            'EXPIRE':  {'min_args': 3, 'max_args': 3, 'usage': 'EXPIRE key seconds',
                       'types': [str, str, int]},
            'SET':     {'min_args': 3, 'max_args': 3, 'usage': 'SET key value'},
            'GET':     {'min_args': 2, 'max_args': 2, 'usage': 'GET key'},
            'DEL':     {'min_args': 2, 'max_args': 2, 'usage': 'DEL key'},
            'LPOP':    {'min_args': 2, 'max_args': 2, 'usage': 'LPOP key'},
            'ECHO':    {'min_args': 2, 'max_args': None, 'usage': 'ECHO message ...'},
            'LPUSH':   {'min_args': 3, 'max_args': 3, 'usage': 'LPUSH key value'},
            'RPUSH':   {'min_args': 3, 'max_args': 3, 'usage': 'RPUSH key value'},
            'INSPECT': {'min_args': 1, 'max_args': 1, 'usage': 'INSPECT'},
        }

    def validate_command(self, command_parts: List[str]) -> Tuple[bool, str]:
        """
        Validate a command against the command registry.
        
        Args:
            command_parts: List of command parts (command name and arguments)
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not command_parts:
            return False, 'Empty command'
            
        command = command_parts[0].upper()
        if command not in self._command_specs:
            return False, f'Unknown command: {command}'
            
        spec = self._command_specs[command]
        num_args = len(command_parts)
        
        # Check argument count
        if num_args < spec['min_args']:
            return False, f'Too few arguments. Usage: {spec["usage"]}'
        if spec['max_args'] and num_args > spec['max_args']:
            return False, f'Too many arguments. Usage: {spec["usage"]}'
            
        # Type validation if specified
        if 'types' in spec:
            try:
                for i, (arg, type_) in enumerate(zip(command_parts[1:], spec['types'][1:]), 1):
                    if type_ == int:
                        int(arg)  # Just try conversion
            except ValueError:
                return False, f'Argument {i} must be a number'
                
        return True, ''

    def get_command_usage(self, command: str) -> str:
        """
        Get the usage string for a command.
        
        Args:
            command: The command to get usage for
            
        Returns:
            str: The usage string for the command or an error message
        """
        command = command.upper()
        if command in self._command_specs:
            return self._command_specs[command]['usage']
        return f'Unknown command: {command}'

    def register_command(self, 
                        command: str,
                        min_args: int,
                        max_args: Optional[int],
                        usage: str,
                        types: Optional[List[Type]] = None) -> None:
        """
        Register a new command specification.
        
        Args:
            command: Command name (will be converted to uppercase)
            min_args: Minimum number of arguments (including command)
            max_args: Maximum number of arguments (including command), None for unlimited
            usage: Usage string for error messages
            types: Optional list of types for arguments
        """
        command = command.upper()
        spec = {
            'min_args': min_args,
            'max_args': max_args,
            'usage': usage
        }
        if types:
            spec['types'] = types
        self._command_specs[command] = spec

    def list_commands(self) -> List[str]:
        """
        Get a list of all registered commands.
        
        Returns:
            List[str]: List of registered command names
        """
        return list(self._command_specs.keys())

    def get_command_spec(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Get the specification for a command.
        
        Args:
            command: The command to get the specification for
            
        Returns:
            Optional[Dict[str, Any]]: The command specification or None if not found
        """
        return self._command_specs.get(command.upper())

# Create default handler instance for convenience
default_handler = ValidationHandler()
validate_command = default_handler.validate_command