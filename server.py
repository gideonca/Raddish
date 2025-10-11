import socket
import threading
from src.expiration_manager import ExpiringDict
from src.command_handler import CommandHandler

# Initialize store and command handler
store = ExpiringDict()
command_handler = CommandHandler(store)

def handle_client_connection(client_socket):
    """Handle client connection and process commands."""
    def send_response(response: bytes):
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