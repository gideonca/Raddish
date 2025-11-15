#!/usr/bin/env python3
"""
Test script to demonstrate logging functionality.
This script connects to the Radish server and executes various commands
to generate log entries.
"""

import socket
import time

def send_command(sock, command):
    """Send a command and receive response."""
    sock.sendall(f"{command}\n".encode())
    response = sock.recv(4096).decode()
    print(f"Command: {command}")
    print(f"Response: {response}")
    print("-" * 50)
    time.sleep(0.1)
    return response

def main():
    """Run test commands to generate log entries."""
    print("Testing Radish Logging Functionality")
    print("=" * 50)
    
    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect(('localhost', 6379))
        print("Connected to Radish server\n")
        
        # Test basic commands
        send_command(sock, "PING")
        send_command(sock, "SET mykey 'Hello World'")
        send_command(sock, "GET mykey")
        send_command(sock, "EXPIRE mykey 300")
        
        # Test cache commands
        send_command(sock, "CREATECACHE testcache")
        send_command(sock, "CACHESET testcache key1 value1")
        send_command(sock, "CACHEGET testcache key1")
        send_command(sock, "LISTCACHES")
        
        # Test error (invalid command)
        send_command(sock, "INVALIDCMD")
        
        # Exit
        send_command(sock, "EXIT")
        
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Is it running?")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nCheck logs at: ~/.radish/logs/radish_<date>.log")
    print("Or use: cat ~/.radish/logs/radish_$(date +%Y-%m-%d).log")

if __name__ == "__main__":
    main()
