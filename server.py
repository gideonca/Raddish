import socket
import threading
import time
from src.expiration_manager import ExpiringDict

# a simple in memory-store
store = ExpiringDict()

def handle_client_connection(client_socket):
    with client_socket:
        while True:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break
            
            command_parts = request.strip().split()
            if not command_parts:
                continue
            
            command = command_parts[0].upper()
            
            # Handle EXIT command to close connection
            if(command_parts[0].upper() == 'EXIT'):
                client_socket.sendall(b'Goodbye!\n')
                break
            
            # Basic command validation, ensuring enough arguments
            if not validate_command(command_parts):
                break;
                
            
            # TODO: Move to a parser module
            match command:
                case 'PING':
                    client_socket.sendall(b'PONG\n')
                case 'ECHO':
                    message = ' '.join(command_parts[1:])
                    client_socket.sendall(f'{message}\n'.encode('utf-8'))
                case 'SET':
                    key, value = command_parts[1], command_parts[2]
                    store.set(key, value)
                    client_socket.sendall(b'OK\n')
                case 'GET':
                    key = command_parts[1]
                    value = store.get(key, 'NULL')
                    client_socket.sendall(f'{value}\n'.encode('utf-8'))
                case 'DEL':
                    key = command_parts[1]
                    if key in store:
                        del store[key]
                        client_socket.sendall(b'OK\n')
                    else:
                        client_socket.sendall(b'NULL\n')
                case 'EXPIRE':
                    key, ttl = command_parts[1], int(command_parts[2])
                    if key in store:
                        value = store.get(key)
                        store.set(key, value, ttl=ttl)
                        client_socket.sendall(b'OK\n')
                case _:
                    client_socket.sendall(b'ERROR: Unknown command\n')
        client_socket.close()
        
def validate_command(command_parts):
    if(not command_parts):
        return False, 'ERROR: Empty command'
    elif(command_parts[0].upper() in ('PING', 'EXIT', 'EXPIRE')):
        return True
    elif(len(command_parts) < 2):
        return False, 'ERROR: Not enough arguments'
    return True, ''

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