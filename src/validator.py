"""
Command validation for the Raddish server.
Provides a registry-based validation system for Redis-like commands.
"""
from typing import Tuple, Dict, Any, List, Optional, Union

# Command validation registry
COMMAND_SPECS: Dict[str, Dict[str, Any]] = {
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

class CommandValidator:
    """Validates Redis-like commands against a specification registry."""
    
    def __init__(self, command_specs: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize the validator with command specifications.
        
        Args:
            command_specs: Optional custom command specifications.
                         If None, uses the default COMMAND_SPECS.
        """
        self.command_specs = command_specs or COMMAND_SPECS

    def validate(self, command_parts: List[str]) -> Tuple[bool, str]:
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
        if command not in self.command_specs:
            return False, f'Unknown command: {command}'
            
        spec = self.command_specs[command]
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

    def get_usage(self, command: str) -> str:
        """Get the usage string for a command."""
        command = command.upper()
        if command in self.command_specs:
            return self.command_specs[command]['usage']
        return f'Unknown command: {command}'

    def register_command(self, 
                        command: str,
                        min_args: int,
                        max_args: Optional[int],
                        usage: str,
                        types: Optional[List[type]] = None) -> None:
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
        self.command_specs[command] = spec

# Global validator instance for convenience
default_validator = CommandValidator()
validate_command = default_validator.validate
