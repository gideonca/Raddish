"""
Test script for CACHEGETALL command.
"""

import socket
import json

def send_command(sock, command):
    """Send a command to the server and return the response."""
    sock.sendall(command.encode('utf-8'))
    response = sock.recv(4096).decode('utf-8')
    return response

def main():
    host = '127.0.0.1'
    port = 6379
    
    print("Testing CACHEGETALL Command")
    print("=" * 50)
    print()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        
        # Create a cache and add some data
        print("1. Adding data to 'users' cache...")
        print(send_command(sock, "CACHESET users user:1 john@example.com"))
        print(send_command(sock, "CACHESET users user:2 jane@example.com"))
        print(send_command(sock, "CACHESET users user:3 bob@example.com"))
        print()
        
        # Add some product data
        print("2. Adding data to 'products' cache...")
        print(send_command(sock, "CACHESET products laptop Dell_XPS"))
        print(send_command(sock, "CACHESET products mouse Logitech_MX"))
        print(send_command(sock, "CACHESET products keyboard Mechanical"))
        print()
        
        # Get all data from users cache
        print("3. Getting all data from 'users' cache:")
        response = send_command(sock, "CACHEGETALL users")
        print(response)
        print()
        
        # Parse and display nicely
        try:
            data = json.loads(response)
            print("Parsed data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        except json.JSONDecodeError:
            print("Note: Response is not JSON")
        print()
        
        # Get all data from products cache
        print("4. Getting all data from 'products' cache:")
        response = send_command(sock, "CACHEGETALL products")
        print(response)
        print()
        
        # Test with empty cache
        print("5. Creating empty cache and testing CACHEGETALL...")
        print(send_command(sock, "CREATECACHE empty"))
        response = send_command(sock, "CACHEGETALL empty")
        print(f"Empty cache result: {response}")
        print()
        
        # Test with non-existent cache
        print("6. Testing with non-existent cache...")
        response = send_command(sock, "CACHEGETALL nonexistent")
        print(f"Non-existent cache result: {response}")
        print()
        
        print("Test complete!")

if __name__ == '__main__':
    main()
