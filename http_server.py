"""
HTTP API wrapper for the Radish server.
No external dependencies required - uses only built-in modules.

This provides a simple HTTP interface to the Radish TCP server,
allowing HTTP clients to interact with the server.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json
from urllib.parse import urlparse, parse_qs
import logging

# Configuration
RADISH_HOST = '127.0.0.1'
RADISH_PORT = 6379
HTTP_PORT = 8000

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def send_command(command):
    """
    Send a command to the Radish server and return the response.
    
    Args:
        command (str): The command to send
        
    Returns:
        str: The server's response
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5.0)  # 5 second timeout
            sock.connect((RADISH_HOST, RADISH_PORT))
            sock.sendall(command.encode('utf-8'))
            response = sock.recv(8192).decode('utf-8')
            return response
    except socket.timeout:
        return "ERROR: Connection timeout"
    except ConnectionRefusedError:
        return "ERROR: Cannot connect to Radish server. Make sure it's running on port 6379"
    except Exception as e:
        return f"ERROR: {str(e)}"


class RadishHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Radish commands."""
    
    def log_message(self, format, *args):
        """Override to use custom logger."""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def _set_headers(self, status=200, content_type='application/json'):
        """Set response headers."""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, data, status=200):
        """Send JSON response."""
        self._set_headers(status)
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def _send_error_json(self, message, status=400):
        """Send error response."""
        self._send_json({"error": message}, status)
    
    def _read_json_body(self):
        """Read and parse JSON from request body."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return {}
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            return None
        except Exception as e:
            logger.error(f"Error reading body: {e}")
            return None
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self._set_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        # Root - API documentation
        if parsed_path.path == '/' or parsed_path.path == '':
            self._send_json({
                "name": "Radish HTTP API",
                "version": "1.0",
                "description": "HTTP interface to Radish server",
                "endpoints": {
                    "GET /": "API documentation",
                    "GET /ping": "Test server connection",
                    "GET /caches": "List all caches",
                    "GET /cache/<name>": "Get all items in a cache (JSON)",
                    "GET /cache/<name>/<key>": "Get specific key from cache",
                    "GET /cache/<name>/keys": "Get all keys in cache",
                    "GET /kv/<key>": "Get value from main store",
                    "POST /cache/<name>": "Set key-value in cache (JSON body: {key, value})",
                    "POST /caches": "Create cache (JSON body: {name})",
                    "POST /kv/<key>": "Set value in main store (JSON body: {value})",
                    "POST /command": "Execute raw command (JSON body: {command})",
                    "DELETE /cache/<name>/<key>": "Delete key from cache",
                    "DELETE /cache/<name>": "Delete entire cache"
                }
            })
            return
        
        # GET /ping
        if path_parts[0] == 'ping':
            response = send_command('PING')
            self._send_json({"status": "ok", "response": response})
            return
        
        # GET /caches - List all caches
        if path_parts[0] == 'caches' and len(path_parts) == 1:
            response = send_command('LISTCACHES')
            self._send_json({"caches": response})
            return
        
        # GET /cache/<name> - Get all items in cache
        if path_parts[0] == 'cache' and len(path_parts) == 2:
            cache_name = path_parts[1]
            response = send_command(f'CACHEGETALL {cache_name}')
            
            # Try to parse as JSON
            try:
                data = json.loads(response)
                self._send_json(data)
            except json.JSONDecodeError:
                self._send_json({"response": response})
            return
        
        # GET /cache/<name>/keys - Get all keys in cache
        if path_parts[0] == 'cache' and len(path_parts) == 3 and path_parts[2] == 'keys':
            cache_name = path_parts[1]
            response = send_command(f'CACHEKEYS {cache_name}')
            keys = [k.strip() for k in response.split('\n') if k.strip() and not k.startswith('No keys')]
            self._send_json({"cache": cache_name, "keys": keys})
            return
        
        # GET /cache/<name>/<key> - Get specific key from cache
        if path_parts[0] == 'cache' and len(path_parts) == 3:
            cache_name, key = path_parts[1], path_parts[2]
            response = send_command(f'CACHEGET {cache_name} {key}')
            self._send_json({"cache": cache_name, "key": key, "value": response})
            return
        
        # GET /kv/<key> - Get value from main store
        if path_parts[0] == 'kv' and len(path_parts) == 2:
            key = path_parts[1]
            response = send_command(f'GET {key}')
            self._send_json({"key": key, "value": response})
            return
        
        # Unknown endpoint
        self._send_error_json("Endpoint not found", 404)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        # Read JSON body
        body = self._read_json_body()
        if body is None:
            self._send_error_json("Invalid JSON in request body")
            return
        
        # POST /caches - Create a cache
        if path_parts[0] == 'caches' and len(path_parts) == 1:
            cache_name = body.get('name')
            if not cache_name:
                self._send_error_json("Missing 'name' in request body")
                return
            
            response = send_command(f'CREATECACHE {cache_name}')
            self._send_json({"response": response})
            return
        
        # POST /cache/<name> - Set key-value in cache
        if path_parts[0] == 'cache' and len(path_parts) == 2:
            cache_name = path_parts[1]
            key = body.get('key')
            value = body.get('value')
            
            if not key or value is None:
                self._send_error_json("Missing 'key' or 'value' in request body")
                return
            
            # Convert dict/list values to JSON string
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            response = send_command(f'CACHESET {cache_name} {key} {value}')
            self._send_json({"response": response, "cache": cache_name, "key": key})
            return
        
        # POST /kv/<key> - Set value in main store
        if path_parts[0] == 'kv' and len(path_parts) == 2:
            key = path_parts[1]
            value = body.get('value')
            
            if value is None:
                self._send_error_json("Missing 'value' in request body")
                return
            
            # Convert dict/list values to JSON string
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            response = send_command(f'SET {key} {value}')
            self._send_json({"response": response, "key": key})
            return
        
        # POST /command - Execute raw command
        if path_parts[0] == 'command' and len(path_parts) == 1:
            command = body.get('command')
            if not command:
                self._send_error_json("Missing 'command' in request body")
                return
            
            response = send_command(command)
            self._send_json({"command": command, "response": response})
            return
        
        # POST /list/<key> - Push to list
        if path_parts[0] == 'list' and len(path_parts) == 2:
            key = path_parts[1]
            value = body.get('value')
            position = body.get('position', 'right')  # 'left' or 'right'
            
            if value is None:
                self._send_error_json("Missing 'value' in request body")
                return
            
            command = 'LPUSH' if position == 'left' else 'RPUSH'
            response = send_command(f'{command} {key} {value}')
            self._send_json({"response": response, "key": key, "position": position})
            return
        
        # Unknown endpoint
        self._send_error_json("Endpoint not found", 404)
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        # DELETE /cache/<name> - Delete entire cache
        if path_parts[0] == 'cache' and len(path_parts) == 2:
            cache_name = path_parts[1]
            response = send_command(f'DELETECACHE {cache_name}')
            self._send_json({"response": response, "cache": cache_name})
            return
        
        # DELETE /cache/<name>/<key> - Delete key from cache
        if path_parts[0] == 'cache' and len(path_parts) == 3:
            cache_name, key = path_parts[1], path_parts[2]
            response = send_command(f'CACHEDEL {cache_name} {key}')
            self._send_json({"response": response, "cache": cache_name, "key": key})
            return
        
        # DELETE /kv/<key> - Delete from main store
        if path_parts[0] == 'kv' and len(path_parts) == 2:
            key = path_parts[1]
            response = send_command(f'DEL {key}')
            self._send_json({"response": response, "key": key})
            return
        
        # Unknown endpoint
        self._send_error_json("Endpoint not found", 404)


def main():
    """Start the HTTP server."""
    server_address = ('', HTTP_PORT)
    httpd = HTTPServer(server_address, RadishHTTPHandler)
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║           Radish HTTP API Server                          ║
╠═══════════════════════════════════════════════════════════╣
║  HTTP Server: http://localhost:{HTTP_PORT}                ║
║  Radish TCP:  {RADISH_HOST}:{RADISH_PORT}                 ║
║                                                           ║
║  No external dependencies required!                       ║
╚═══════════════════════════════════════════════════════════╝

Make sure the Radish TCP server is running on port {RADISH_PORT}

Example requests:
  curl http://localhost:{HTTP_PORT}/ping
  curl http://localhost:{HTTP_PORT}/caches
  curl -X POST -H 'Content-Type: application/json' \\
       -d '{{"name":"users"}}' \\
       http://localhost:{HTTP_PORT}/caches
  curl -X POST -H 'Content-Type: application/json' \\
       -d '{{"key":"user1","value":"john@example.com"}}' \\
       http://localhost:{HTTP_PORT}/cache/users
  curl http://localhost:{HTTP_PORT}/cache/users

Starting server...
""")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()
        print("Server stopped.")


if __name__ == '__main__':
    main()
