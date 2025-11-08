#!/bin/bash

# Test script for vanilla Python HTTP API
# No external dependencies required!

API_URL="http://localhost:8000"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Testing Radish HTTP API (Vanilla Python)             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Test 1: API Documentation
echo "1. Getting API documentation..."
curl -s $API_URL/ | python3 -m json.tool
echo ""

# Test 2: Ping
echo "2. Testing server connection..."
curl -s $API_URL/ping | python3 -m json.tool
echo ""

# Test 3: Create a cache
echo "3. Creating 'users' cache..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"users"}' \
  $API_URL/caches | python3 -m json.tool
echo ""

# Test 4: Add items to cache
echo "4. Adding users to cache..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1","value":"john@example.com"}' \
  $API_URL/cache/users | python3 -m json.tool

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"key":"user2","value":"jane@example.com"}' \
  $API_URL/cache/users | python3 -m json.tool

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"key":"user3","value":"bob@example.com"}' \
  $API_URL/cache/users | python3 -m json.tool
echo ""

# Test 5: Get all items from cache
echo "5. Getting all users from cache..."
curl -s $API_URL/cache/users | python3 -m json.tool
echo ""

# Test 6: Get a specific item
echo "6. Getting user1..."
curl -s $API_URL/cache/users/user1 | python3 -m json.tool
echo ""

# Test 7: Get all cache keys
echo "7. Getting all keys in users cache..."
curl -s $API_URL/cache/users/keys | python3 -m json.tool
echo ""

# Test 8: Create another cache with complex data
echo "8. Creating 'products' cache with JSON data..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"products"}' \
  $API_URL/caches | python3 -m json.tool

curl -s -X POST -H "Content-Type: application/json" \
  -d '{"key":"laptop","value":{"name":"Dell XPS","price":1200,"inStock":true}}' \
  $API_URL/cache/products | python3 -m json.tool
echo ""

# Test 9: Get all products
echo "9. Getting all products..."
curl -s $API_URL/cache/products | python3 -m json.tool
echo ""

# Test 10: List all caches
echo "10. Listing all caches..."
curl -s $API_URL/caches | python3 -m json.tool
echo ""

# Test 11: Delete a key
echo "11. Deleting user2..."
curl -s -X DELETE $API_URL/cache/users/user2 | python3 -m json.tool
echo ""

# Test 12: Get all users again
echo "12. Getting all users after deletion..."
curl -s $API_URL/cache/users | python3 -m json.tool
echo ""

# Test 13: Execute raw command
echo "13. Executing raw LISTCACHES command..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"command":"LISTCACHES"}' \
  $API_URL/command | python3 -m json.tool
echo ""

# Test 14: Work with main key-value store
echo "14. Setting value in main store..."
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"value":"Hello World"}' \
  $API_URL/kv/greeting | python3 -m json.tool

echo "Getting value from main store..."
curl -s $API_URL/kv/greeting | python3 -m json.tool
echo ""

# Test 15: Delete entire cache
echo "15. Deleting products cache..."
curl -s -X DELETE $API_URL/cache/products | python3 -m json.tool
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    Test Complete!                         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
