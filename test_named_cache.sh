#!/bin/bash

# Test script for named cache functionality

echo "Testing Named Cache System"
echo "=========================="
echo ""

# Function to send a command and display the result
send_command() {
    echo "Command: $1"
    echo "$1" | nc localhost 6379
    echo ""
    sleep 0.1
}

# Create named caches
echo "1. Creating named caches..."
send_command "CREATECACHE users"
send_command "CREATECACHE products"
send_command "CREATECACHE sessions"

# List all caches
echo "2. Listing all caches..."
send_command "LISTCACHES"

# Add key-value pairs to the 'users' cache
echo "3. Adding data to 'users' cache..."
send_command "CACHESET users user1 john@example.com"
send_command "CACHESET users user2 jane@example.com"
send_command "CACHESET users user3 bob@example.com"

# Add key-value pairs to the 'products' cache
echo "4. Adding data to 'products' cache..."
send_command "CACHESET products prod1 laptop"
send_command "CACHESET products prod2 phone"

# Get values from caches
echo "5. Retrieving values from caches..."
send_command "CACHEGET users user1"
send_command "CACHEGET products prod1"

# List all keys in a cache
echo "6. Listing keys in 'users' cache..."
send_command "CACHEKEYS users"

# List all keys in a cache
echo "7. Listing keys in 'products' cache..."
send_command "CACHEKEYS products"

# Check cache sizes
echo "8. Checking cache sizes..."
send_command "LISTCACHES"

# Delete a key from a cache
echo "9. Deleting a key from 'users' cache..."
send_command "CACHEDEL users user2"
send_command "CACHEKEYS users"

# Delete a cache
echo "10. Deleting 'sessions' cache..."
send_command "DELETECACHE sessions"
send_command "LISTCACHES"

echo "Test complete!"
