"""
Example demonstrating named cache functionality.

This example shows how to:
1. Create named caches
2. Store key-value pairs in specific caches
3. Retrieve values from caches by name
4. List all keys in a cache
5. Delete keys and caches
"""

import socket
import time

def send_command(sock, command):
    """Send a command to the server and return the response."""
    sock.sendall(command.encode('utf-8'))
    response = sock.recv(4096).decode('utf-8')
    return response

def main():
    # Connect to the server
    host = '127.0.0.1'
    port = 6379
    
    print("Named Cache Example")
    print("=" * 50)
    print()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        
        # 1. Create named caches for different purposes
        print("1. Creating named caches...")
        print(send_command(sock, "CREATECACHE users"))
        print(send_command(sock, "CREATECACHE products"))
        print(send_command(sock, "CREATECACHE sessions"))
        print()
        
        # 2. List all caches
        print("2. Available caches:")
        print(send_command(sock, "LISTCACHES"))
        print()
        
        # 3. Store user data in 'users' cache
        print("3. Storing user data...")
        print(send_command(sock, "CACHESET users user:1 john@example.com"))
        print(send_command(sock, "CACHESET users user:2 jane@example.com"))
        print(send_command(sock, "CACHESET users user:3 bob@example.com"))
        print()
        
        # 4. Store product data in 'products' cache
        print("4. Storing product data...")
        print(send_command(sock, "CACHESET products item:100 Laptop"))
        print(send_command(sock, "CACHESET products item:101 Mouse"))
        print(send_command(sock, "CACHESET products item:102 Keyboard"))
        print()
        
        # 5. Store session data in 'sessions' cache
        print("5. Storing session data...")
        print(send_command(sock, "CACHESET sessions sess:abc123 user:1"))
        print(send_command(sock, "CACHESET sessions sess:def456 user:2"))
        print()
        
        # 6. Retrieve values from specific caches
        print("6. Retrieving data from caches...")
        print(f"User 1: {send_command(sock, 'CACHEGET users user:1')}")
        print(f"Product 100: {send_command(sock, 'CACHEGET products item:100')}")
        print(f"Session abc123: {send_command(sock, 'CACHEGET sessions sess:abc123')}")
        print()
        
        # 7. List all keys in each cache
        print("7. Keys in 'users' cache:")
        print(send_command(sock, "CACHEKEYS users"))
        print()
        
        print("8. Keys in 'products' cache:")
        print(send_command(sock, "CACHEKEYS products"))
        print()
        
        # 9. Check cache sizes
        print("9. Cache sizes:")
        print(send_command(sock, "LISTCACHES"))
        print()
        
        # 10. Delete a key from a cache
        print("10. Deleting user:2 from users cache...")
        print(send_command(sock, "CACHEDEL users user:2"))
        print("Updated keys in 'users' cache:")
        print(send_command(sock, "CACHEKEYS users"))
        print()
        
        # 11. Delete an entire cache
        print("11. Deleting 'sessions' cache...")
        print(send_command(sock, "DELETECACHE sessions"))
        print("Remaining caches:")
        print(send_command(sock, "LISTCACHES"))
        print()
        
        # 12. Try to access deleted cache
        print("12. Trying to access deleted cache...")
        print(send_command(sock, "CACHEGET sessions sess:abc123"))
        print()
        
        print("Example complete!")

if __name__ == '__main__':
    main()
