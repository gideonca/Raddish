"""
A Redis-like server implementation that supports basic key-value operations with expiration.

This module implements a TCP server that handles client connections and processes Redis-style
commands. It supports concurrent connections through threading and provides basic Redis
commands like SET, GET, DEL, EXPIRE, and RPUSH.

The server maintains data in an ExpiringStore which automatically handles key expiration.
"""

import socket
import threading
from src.expiring_store import ExpiringStore
from src.command_handler import CommandHandler

# Initialize store and command handler
store = ExpiringStore()
command_handler = CommandHandler(store)

def handle_client_connection(client_socket):
    """
    Handle individual client connections and process their commands.
    
    This function runs in a separate thread for each client connection. It reads
    commands from the client socket, processes them through the command handler,
    and sends back appropriate responses.
    
    Args:
        client_socket (socket.socket): The connected client socket to handle
        
    Note:
        The connection is automatically closed when the client disconnects or
        sends an EXIT command.
    """
    def send_response(response: bytes):
        """
        Send a response back to the client.
        
        Args:
            response (bytes): The response to send to the client
        """
        client_socket.sendall(response)
        
    with client_socket:
        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            
            command_parts = request.strip().split()
            if not command_parts:
                continue
                
            # Process command and check if we should continue
            if not command_handler.handle_command(command_parts, send_response):
                break
                
        client_socket.close()

def start_server(host='127.0.0.1', port=6379):
    """
    Start the server and listen for client connections.
    
    Creates a TCP server that listens for incoming connections and spawns a new
    thread for each client connection.
    
    Args:
        host (str, optional): The host address to bind to. Defaults to '127.0.0.1'.
        port (int, optional): The port to listen on. Defaults to 6379 (Redis default port).
        
    Raises:
        OSError: If the server cannot bind to the specified host and port
        KeyboardInterrupt: If the server is manually stopped with Ctrl+C
        
    Note:
        The server runs indefinitely until interrupted. Each client connection
        is handled in a separate thread.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f'Server listening on {host}:{port}')
    
    try:
        while True:
            client_socket, addr = server.accept()
            print(f'Accepted connection from {addr}')
            client_handler = threading.Thread(
                target=handle_client_connection,
                args=(client_socket,)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print('Shutting down server.')
    finally:
        server.close()
        
if __name__ == '__main__':
    start_server()