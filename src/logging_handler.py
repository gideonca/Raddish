import os
import logging
from datetime import datetime
from pathlib import Path
import threading


class LoggingHandler:
    """
    Handles logging of all Radish commands, responses, and events.
    Logs are stored in /.radish/logs/ directory with daily rotation.
    """
    
    def __init__(self, log_dir: str = None):
        """
        Initialize the logging handler.
        
        Args:
            log_dir: Custom log directory path. If None, uses /.radish/logs/
        """
        self.lock = threading.Lock()
        
        # Set up log directory
        if log_dir is None:
            # Use root directory: /.radish/logs
            self.log_dir = Path("/") / ".radish" / "logs"
        else:
            self.log_dir = Path(log_dir)
        
        # Create log directory if it doesn't exist
        self._create_log_directory()
        
        # Set up logger
        self.logger = self._setup_logger()
        
        # In-memory log buffer for get_logs()
        self.logs = []
        self.max_memory_logs = 1000  # Keep last 1000 logs in memory
    
    def _create_log_directory(self):
        """Create the log directory with proper permissions."""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            # Set permissions to allow writing (755)
            os.chmod(self.log_dir, 0o755)
        except PermissionError:
            # Fallback to home directory if root is not writable
            fallback_dir = Path.home() / ".radish" / "logs"
            print(f"Warning: Cannot write to {self.log_dir}. Using fallback: {fallback_dir}")
            self.log_dir = fallback_dir
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directory: {e}")
            # Use current directory as last resort
            self.log_dir = Path(".") / "logs"
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self):
        """Set up the file logger with daily rotation."""
        logger = logging.getLogger('radish')
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create daily log file
        log_file = self._get_log_file_path()
        
        # File handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format: [2025-11-14 15:30:45.123] LEVEL - Message
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        return logger
    
    def _get_log_file_path(self):
        """Get the log file path for today."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.log_dir / f"radish_{today}.log"
    
    def _add_to_memory(self, message: str):
        """Add log to in-memory buffer with size limit."""
        with self.lock:
            self.logs.append(message)
            # Keep only the last max_memory_logs entries
            if len(self.logs) > self.max_memory_logs:
                self.logs = self.logs[-self.max_memory_logs:]
    
    def log_command(self, client_addr: tuple, command: str):
        """
        Log a received command.
        
        Args:
            client_addr: Tuple of (host, port) for the client
            command: The command string received
        """
        timestamp = datetime.now()
        client_str = f"{client_addr[0]}:{client_addr[1]}"
        message = f"COMMAND from {client_str}: {command}"
        
        with self.lock:
            self.logger.info(message)
            self._add_to_memory(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    def log_response(self, client_addr: tuple, response: str, command: str = None):
        """
        Log a response sent to client.
        
        Args:
            client_addr: Tuple of (host, port) for the client
            response: The response string sent
            command: Optional command that generated this response
        """
        timestamp = datetime.now()
        client_str = f"{client_addr[0]}:{client_addr[1]}"
        
        if command:
            message = f"RESPONSE to {client_str} for '{command}': {response}"
        else:
            message = f"RESPONSE to {client_str}: {response}"
        
        with self.lock:
            self.logger.info(message)
            self._add_to_memory(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    def log_error(self, client_addr: tuple, error: str, command: str = None):
        """
        Log an error.
        
        Args:
            client_addr: Tuple of (host, port) for the client
            error: The error message
            command: Optional command that caused the error
        """
        timestamp = datetime.now()
        client_str = f"{client_addr[0]}:{client_addr[1]}"
        
        if command:
            message = f"ERROR for {client_str} on '{command}': {error}"
        else:
            message = f"ERROR for {client_str}: {error}"
        
        with self.lock:
            self.logger.error(message)
            self._add_to_memory(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] ERROR - {message}")
    
    def log_connection(self, client_addr: tuple, event: str = "CONNECTED"):
        """
        Log client connection events.
        
        Args:
            client_addr: Tuple of (host, port) for the client
            event: Event type (CONNECTED, DISCONNECTED)
        """
        timestamp = datetime.now()
        client_str = f"{client_addr[0]}:{client_addr[1]}"
        message = f"CLIENT {event}: {client_str}"
        
        with self.lock:
            self.logger.info(message)
            self._add_to_memory(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    def log_server_event(self, event: str):
        """
        Log server-level events.
        
        Args:
            event: Event description (e.g., "Server started", "Cleanup completed")
        """
        timestamp = datetime.now()
        message = f"SERVER: {event}"
        
        with self.lock:
            self.logger.info(message)
            self._add_to_memory(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    def log(self, message: str):
        """
        Generic logging method for backwards compatibility.
        
        Args:
            message: Message to log
        """
        timestamp = datetime.now()
        
        with self.lock:
            self.logger.info(message)
            self._add_to_memory(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}")
    
    def get_logs(self, count: int = None):
        """
        Get recent logs from memory buffer.
        
        Args:
            count: Number of recent logs to return. If None, returns all.
        
        Returns:
            List of log messages
        """
        with self.lock:
            if count is None:
                return self.logs.copy()
            else:
                return self.logs[-count:] if count > 0 else []
    
    def get_log_file_path(self):
        """
        Get the current log file path.
        
        Returns:
            Path object for today's log file
        """
        return self._get_log_file_path()
    
    def get_all_log_files(self):
        """
        Get list of all log files in the log directory.
        
        Returns:
            List of Path objects for all log files
        """
        try:
            return sorted(self.log_dir.glob("radish_*.log"))
        except Exception as e:
            self.logger.error(f"Error listing log files: {e}")
            return []
    
    def read_log_file(self, date: str = None):
        """
        Read contents of a specific log file.
        
        Args:
            date: Date string in YYYY-MM-DD format. If None, reads today's log.
        
        Returns:
            String contents of the log file, or None if file doesn't exist
        """
        if date is None:
            log_file = self._get_log_file_path()
        else:
            log_file = self.log_dir / f"radish_{date}.log"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"Error reading log file {log_file}: {e}")
            return None
    
    def clear_memory_logs(self):
        """Clear the in-memory log buffer."""
        with self.lock:
            self.logs.clear()
    
    def rotate_old_logs(self, days: int = 30):
        """
        Delete log files older than specified days.
        
        Args:
            days: Number of days to keep logs
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days * 86400)
            
            for log_file in self.get_all_log_files():
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            self.logger.error(f"Error rotating logs: {e}")