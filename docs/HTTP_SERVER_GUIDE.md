# HTTP Server Guide

This guide explains how to use the vanilla Python HTTP server to interact with Radish over HTTP.

## Overview

The `http_server_vanilla.py` provides an HTTP REST API wrapper around the Radish TCP server. It uses **only Python's built-in modules** - no external dependencies required!

## Features

- ✅ **Zero dependencies** - Uses only Python standard library
- ✅ **RESTful API** - Clean HTTP endpoints
- ✅ **JSON support** - Handles complex data structures
- ✅ **CORS enabled** - Works with web browsers and cross-origin requests
- ✅ **Full feature support** - All Radish commands available via HTTP
- ✅ **Auto-documentation** - Built-in API reference

## Quick Start

### Step 1: Start the Radish TCP Server

In one terminal:
```bash
python server.py
```

The TCP server will start on port **6379** (default Redis port).

### Step 2: Start the HTTP Server

In another terminal:
```bash
python http_server_vanilla.py
```

The HTTP API will be available at **http://localhost:8000**

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║           Radish HTTP API Server (Vanilla Python)         ║
╠═══════════════════════════════════════════════════════════╣
║  HTTP Server: http://localhost:8000                       ║
║  Radish TCP:  127.0.0.1:6379                              ║
║                                                           ║
║  No external dependencies required!                       ║
╚═══════════════════════════════════════════════════════════╝
```

### Step 3: Test the Connection

```bash
curl http://localhost:8000/ping
```

You should get:
```json
{
  "status": "ok",
  "response": "PONG"
}
```

## API Endpoints

### Server Health

#### GET /
Get API documentation and available endpoints.

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "name": "Radish HTTP API",
  "version": "1.0",
  "description": "HTTP interface to Radish server (vanilla Python)",
  "endpoints": {
    "GET /": "API documentation",
    "GET /ping": "Test server connection",
    ...
  }
}
```

#### GET /ping
Test server connection.

**Request:**
```bash
curl http://localhost:8000/ping
```

**Response:**
```json
{
  "status": "ok",
  "response": "PONG"
}
```

---

### Cache Management

#### GET /caches
List all caches.

**Request:**
```bash
curl http://localhost:8000/caches
```

**Response:**
```json
{
  "caches": "Available caches:\n- users (3 items)\n- products (5 items)"
}
```

#### POST /caches
Create a new cache.

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"users"}' \
  http://localhost:8000/caches
```

**Response:**
```json
{
  "response": "OK"
}
```

#### DELETE /cache/{cache_name}
Delete an entire cache.

**Request:**
```bash
curl -X DELETE http://localhost:8000/cache/users
```

**Response:**
```json
{
  "response": "OK",
  "cache": "users"
}
```

---

### Cache Operations

#### GET /cache/{cache_name}
Get all key-value pairs in a cache as JSON.

**Request:**
```bash
curl http://localhost:8000/cache/users
```

**Response:**
```json
{
  "user1": "john@example.com",
  "user2": "jane@example.com",
  "user3": "bob@example.com"
}
```

#### GET /cache/{cache_name}/{key}
Get a specific key from a cache.

**Request:**
```bash
curl http://localhost:8000/cache/users/user1
```

**Response:**
```json
{
  "cache": "users",
  "key": "user1",
  "value": "john@example.com"
}
```

#### GET /cache/{cache_name}/keys
Get all keys in a cache.

**Request:**
```bash
curl http://localhost:8000/cache/users/keys
```

**Response:**
```json
{
  "cache": "users",
  "keys": ["user1", "user2", "user3"]
}
```

#### POST /cache/{cache_name}
Set a key-value pair in a cache.

**Request with simple value:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1","value":"john@example.com"}' \
  http://localhost:8000/cache/users
```

**Request with JSON object:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1","value":{"name":"John Doe","age":30,"email":"john@example.com"}}' \
  http://localhost:8000/cache/users
```

**Response:**
```json
{
  "response": "OK",
  "cache": "users",
  "key": "user1"
}
```

#### DELETE /cache/{cache_name}/{key}
Delete a key from a cache.

**Request:**
```bash
curl -X DELETE http://localhost:8000/cache/users/user1
```

**Response:**
```json
{
  "response": "OK",
  "cache": "users",
  "key": "user1"
}
```

---

### Key-Value Store Operations

#### GET /kv/{key}
Get a value from the main store.

**Request:**
```bash
curl http://localhost:8000/kv/greeting
```

**Response:**
```json
{
  "key": "greeting",
  "value": "Hello World"
}
```

#### POST /kv/{key}
Set a value in the main store.

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"value":"Hello World"}' \
  http://localhost:8000/kv/greeting
```

**Response:**
```json
{
  "response": "OK",
  "key": "greeting"
}
```

#### DELETE /kv/{key}
Delete a key from the main store.

**Request:**
```bash
curl -X DELETE http://localhost:8000/kv/greeting
```

**Response:**
```json
{
  "response": "OK",
  "key": "greeting"
}
```

---

### List Operations

#### POST /list/{key}
Push a value to a list.

**Push to the right (end) of list:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"value":"item1","position":"right"}' \
  http://localhost:8000/list/mylist
```

**Push to the left (beginning) of list:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"value":"item0","position":"left"}' \
  http://localhost:8000/list/mylist
```

**Response:**
```json
{
  "response": "OK",
  "key": "mylist",
  "position": "right"
}
```

---

### Raw Command Execution

#### POST /command
Execute a raw Radish command.

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"command":"INSPECT"}' \
  http://localhost:8000/command
```

**Response:**
```json
{
  "command": "INSPECT",
  "response": "key1: value1\nkey2: value2\nEND"
}
```

---

## Complete Examples

### Example 1: User Management System

```bash
# Create a cache for users
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"users"}' \
  http://localhost:8000/caches

# Add users with JSON data
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1","value":{"name":"John Doe","email":"john@example.com","role":"admin"}}' \
  http://localhost:8000/cache/users

curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user2","value":{"name":"Jane Smith","email":"jane@example.com","role":"user"}}' \
  http://localhost:8000/cache/users

# Get all users
curl http://localhost:8000/cache/users

# Get specific user
curl http://localhost:8000/cache/users/user1

# List all user IDs
curl http://localhost:8000/cache/users/keys

# Update a user
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1","value":{"name":"John Doe","email":"john@example.com","role":"superadmin"}}' \
  http://localhost:8000/cache/users

# Delete a user
curl -X DELETE http://localhost:8000/cache/users/user2
```

### Example 2: Product Catalog

```bash
# Create products cache
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"products"}' \
  http://localhost:8000/caches

# Add products
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"laptop","value":{"name":"Dell XPS 13","price":1200,"stock":15,"category":"Electronics"}}' \
  http://localhost:8000/cache/products

curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"mouse","value":{"name":"Logitech MX Master","price":80,"stock":50,"category":"Accessories"}}' \
  http://localhost:8000/cache/products

# Get all products
curl http://localhost:8000/cache/products

# Search for a product
curl http://localhost:8000/cache/products/laptop
```

### Example 3: Session Management

```bash
# Create sessions cache
curl -X POST -H "Content-Type: application/json" \
  -d '{"name":"sessions"}' \
  http://localhost:8000/caches

# Store session data
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"sess_abc123","value":{"userId":"user1","loginTime":"2025-11-08T10:00:00Z","lastActivity":"2025-11-08T10:30:00Z"}}' \
  http://localhost:8000/cache/sessions

# Retrieve session
curl http://localhost:8000/cache/sessions/sess_abc123

# End session (delete)
curl -X DELETE http://localhost:8000/cache/sessions/sess_abc123
```

---

## Using from Different Languages

### JavaScript (Browser or Node.js)

```javascript
// Using fetch API
async function addUser(username, userData) {
  const response = await fetch('http://localhost:8000/cache/users', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      key: username,
      value: userData
    })
  });
  return response.json();
}

async function getAllUsers() {
  const response = await fetch('http://localhost:8000/cache/users');
  return response.json();
}

// Usage
await addUser('user1', {
  name: 'John Doe',
  email: 'john@example.com',
  role: 'admin'
});

const users = await getAllUsers();
console.log(users);
```

### Python (using built-in urllib)

```python
import urllib.request
import json

def add_user(username, user_data):
    url = 'http://localhost:8000/cache/users'
    data = json.dumps({'key': username, 'value': user_data}).encode('utf-8')
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get_all_users():
    url = 'http://localhost:8000/cache/users'
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode('utf-8'))

# Usage
add_user('user1', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'role': 'admin'
})

users = get_all_users()
print(users)
```

### Python (using requests library)

```python
import requests

# Add a user
response = requests.post(
    'http://localhost:8000/cache/users',
    json={'key': 'user1', 'value': {'name': 'John Doe', 'email': 'john@example.com'}}
)
print(response.json())

# Get all users
response = requests.get('http://localhost:8000/cache/users')
users = response.json()
print(users)

# Get specific user
response = requests.get('http://localhost:8000/cache/users/user1')
print(response.json())
```

---

## Testing

### Automated Test Script

Run the included test script to verify all endpoints:

```bash
./test_vanilla_http.sh
```

### Python Client Example

Run the example Python client:

```bash
python example_vanilla_http_client.py
```

This demonstrates all API operations programmatically.

---

## Error Handling

### HTTP Status Codes

- **200** - Success
- **400** - Bad Request (missing parameters, invalid JSON)
- **404** - Not Found (invalid endpoint)
- **500** - Server Error

### Error Response Format

All errors return a JSON object with an `error` field:

```json
{
  "error": "Missing 'key' or 'value' in request body"
}
```

### Common Errors

**Missing JSON body:**
```bash
curl -X POST http://localhost:8000/cache/users
```
Response:
```json
{
  "error": "Invalid JSON in request body"
}
```

**Missing required field:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1"}' \
  http://localhost:8000/cache/users
```
Response:
```json
{
  "error": "Missing 'key' or 'value' in request body"
}
```

**Cache doesn't exist:**
```bash
curl http://localhost:8000/cache/nonexistent
```
Response:
```json
{
  "response": "Cache nonexistent does not exist"
}
```

---

## Configuration

### Changing Ports

Edit `http_server_vanilla.py`:

```python
# Configuration
RADISH_HOST = '127.0.0.1'
RADISH_PORT = 6379  # Radish TCP port
HTTP_PORT = 8000    # HTTP API port
```

### Logging

The server uses Python's built-in logging module. All requests are logged with timestamps:

```
2025-11-08 10:30:15 - 127.0.0.1 - "GET /ping HTTP/1.1" 200 -
2025-11-08 10:30:20 - 127.0.0.1 - "POST /cache/users HTTP/1.1" 200 -
```

---

## CORS Support

CORS (Cross-Origin Resource Sharing) is **enabled by default**, allowing requests from web browsers on different origins.

All responses include:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

This means you can make requests from any web application running on a different domain.

---

## Tips and Best Practices

### 1. Auto-Create Caches
Caches are automatically created when you use `CACHESET`. You don't need to explicitly create them:

```bash
# This works even if 'users' cache doesn't exist yet
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"user1","value":"john@example.com"}' \
  http://localhost:8000/cache/users
```

### 2. JSON Values
Complex values (objects, arrays) are automatically serialized:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"config","value":{"timeout":30,"retries":3,"endpoints":["api1","api2"]}}' \
  http://localhost:8000/cache/settings
```

### 3. Use CACHEGETALL for Efficiency
Instead of getting individual keys, use the cache endpoint to get all data at once:

```bash
# More efficient than multiple GET requests
curl http://localhost:8000/cache/users
```

### 4. Raw Commands
For advanced operations, use the `/command` endpoint to execute any Radish command:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"command":"EXPIRE mykey 60"}' \
  http://localhost:8000/command
```

---

## Troubleshooting

### Server Won't Start

**Problem:** `Address already in use`

**Solution:** Another process is using port 8000. Either:
1. Stop the other process
2. Change `HTTP_PORT` in the configuration
3. Find and kill the process: `lsof -ti:8000 | xargs kill`

### Cannot Connect to Radish

**Problem:** `ERROR: Cannot connect to Radish server`

**Solution:** Make sure the Radish TCP server is running:
```bash
python server.py
```

### Timeout Errors

**Problem:** `ERROR: Connection timeout`

**Solution:** The request took too long. Default timeout is 5 seconds. Check if the Radish server is responsive.

---

## Advanced Usage

### Running on Different Host

To accept connections from other machines:

```python
# In http_server_vanilla.py, change:
server_address = ('0.0.0.0', HTTP_PORT)  # Listen on all interfaces
```

Then access from other machines using:
```bash
curl http://<server-ip>:8000/ping
```

### Behind a Reverse Proxy

You can run the HTTP server behind nginx or Apache:

**nginx example:**
```nginx
location /radish/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## See Also

- [Named Cache Guide](NAMED_CACHE_GUIDE.md) - Detailed cache system documentation
- [Main README](../README.md) - Project overview
- `example_vanilla_http_client.py` - Python client implementation
- `test_vanilla_http.sh` - Complete test suite
