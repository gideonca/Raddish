# Radish User Guide

A comprehensive guide to using Radish, a lightweight Redis-like in-memory data store implementation in Python.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Operations](#basic-operations)
- [Working with Lists](#working-with-lists)
- [Named Caches](#named-caches)
- [Expiring Stores](#expiring-stores)
- [Command Validation](#command-validation)
- [Event System](#event-system)
- [Command Reference](#command-reference)
- [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gideonca/radish.git
cd radish
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Note: Radish has no external dependencies - it uses only Python's standard library.

### Starting the Server

Start the Radish server on the default port (6379):

```bash
python server.py
```

The server will start and listen for connections:
```
Radish server starting on 0.0.0.0:6379
Press Ctrl+C to stop
```

### Connecting to the Server

#### Using Telnet

Connect to Radish using telnet:

```bash
telnet localhost 6379
```

To exit the telnet session:
1. Type `EXIT` command, or
2. Press `Ctrl+]` and then type `quit`

#### Using Python

See the [HTTP Server Guide](HTTP_SERVER_GUIDE.md) for HTTP API access, or use a custom TCP client.

## Basic Operations

### PING - Test Connection

Verify the server is responding:

```
> PING
PONG
```

### SET - Store a Value

Set a key-value pair:

```
> SET mykey "Hello World"
OK
> SET username "alice"
OK
> SET counter 42
OK
```

### GET - Retrieve a Value

Get the value for a key:

```
> GET mykey
Hello World
> GET username
alice
> GET counter
42
```

If the key doesn't exist:
```
> GET nonexistent
(nil)
```

### DEL - Delete a Key

Remove a key and its value:

```
> SET temp "temporary data"
OK
> DEL temp
OK
> GET temp
(nil)
```

### EXPIRE - Set Time-To-Live

Set an expiration time (in seconds) for a key:

```
> SET session_token "abc123"
OK
> EXPIRE session_token 60
OK
```

After 60 seconds, the key will automatically be deleted.

### INSPECT - View All Keys

Show all key-value pairs in the default store:

```
> INSPECT
mykey: Hello World
username: alice
counter: 42
```

## Working with Lists

Radish supports list data structures with push and pop operations.

### RPUSH - Append to List

Add an element to the end of a list:

```
> RPUSH mylist "first"
OK
> RPUSH mylist "second"
OK
> RPUSH mylist "third"
OK
```

### LPUSH - Prepend to List

Add an element to the start of a list:

```
> LPUSH mylist "start"
OK
```

Now the list is: `["start", "first", "second", "third"]`

### LPOP - Remove from Front

Remove and return the first element:

```
> LPOP mylist
start
```

## Working with JSON Data

Radish handles JSON data seamlessly. You can include spaces in your JSON strings:

```
> SET user:1 {"name":"John"}
OK

> SET user:2 {"name": "Jane", "age": 25}
OK

> SET user:3 {
    "name": "Bob",
    "age": 30,
    "roles": ["admin", "user"]
}
OK

> GET user:2
{"name": "Jane", "age": 25}
```

## Named Caches

Named caches provide isolated namespaces for organizing your data. Each cache is completely independent.

### Benefits of Named Caches

- **Isolation**: Keep different types of data separate
- **Organization**: Group related data together
- **Bulk Operations**: Delete all data in a cache at once
- **No Key Conflicts**: Same key name can exist in different caches

### Creating Caches

Use `CREATECACHE` to create a new named cache:

```
> CREATECACHE users
OK
> CREATECACHE products
OK
> CREATECACHE sessions
OK
```

### Listing Caches

View all caches and their sizes:

```
> LISTCACHES
Available caches:
- users (0 items)
- products (0 items)
- sessions (0 items)
```

### Working with Cache Data

#### CACHESET - Store in Cache

Store key-value pairs in a specific cache:

```
> CACHESET users user:1 john@example.com
OK
> CACHESET users user:2 jane@example.com
OK
> CACHESET products item:100 Laptop
OK
> CACHESET products item:101 Mouse
OK
```

#### CACHEGET - Retrieve from Cache

Get values from a specific cache:

```
> CACHEGET users user:1
john@example.com
> CACHEGET products item:100
Laptop
```

#### CACHEKEYS - List Cache Keys

List all keys in a cache:

```
> CACHEKEYS users
user:1
user:2
```

#### CACHEGETALL - Get All Cache Data

Retrieve all key-value pairs from a cache as JSON:

```
> CACHEGETALL users
{"user:1": "john@example.com", "user:2": "jane@example.com"}
```

#### CACHEDEL - Delete from Cache

Delete a specific key from a cache:

```
> CACHEDEL users user:2
OK
> CACHEKEYS users
user:1
```

### Deleting Caches

Remove an entire cache and all its contents:

```
> DELETECACHE sessions
OK
```

### Example Workflow

Here's a complete example of using named caches:

```
# Organize user sessions and product data separately
> CREATECACHE user_sessions
OK
> CREATECACHE product_catalog
OK

# Store session data
> CACHESET user_sessions sess:abc123 user:1
OK
> CACHESET user_sessions sess:def456 user:2
OK

# Store product data
> CACHESET product_catalog laptop {"name": "Dell XPS", "price": 1200}
OK
> CACHESET product_catalog mouse {"name": "Logitech MX", "price": 80}
OK

# Retrieve and manage data
> CACHEGET user_sessions sess:abc123
user:1
> CACHEKEYS product_catalog
laptop
mouse

# Check cache sizes
> LISTCACHES
Available caches:
- user_sessions (2 items)
- product_catalog (2 items)

# Get all products as JSON
> CACHEGETALL product_catalog
{"laptop": "{\"name\": \"Dell XPS\", \"price\": 1200}", "mouse": "{\"name\": \"Logitech MX\", \"price\": 80}"}
```

For more details, see the [Named Cache Guide](NAMED_CACHE_GUIDE.md).

## Expiring Stores (Advanced)

Expiring stores provide a hierarchical organization system with automatic TTL support.

### Creating Stores

Create a store within a cache, optionally with a TTL:

```
> CREATESTORE users temp_tokens 3600  # Create store with 1-hour TTL
OK
> CREATESTORE users profiles          # Create store with no TTL
OK
```

### Listing Stores

View all stores in a cache:

```
> LISTSTORES users
Stores in cache users:
- temp_tokens (0 items, 3600 TTL)
- profiles (0 items, No TTL)
```

### Using Stores

Access stores using the `cache:store:key` format:

```
> SET users:temp_tokens:123 "session_abc"
OK
> SET users:profiles:456 {"name": "John"}
OK
> GET users:temp_tokens:123
session_abc
```

### Deleting Stores

Remove a store and all its contents:

```
> DELETESTORE users temp_tokens
OK
```

## Command Validation

Radish includes a robust command validation system that ensures command integrity.

### Validation Features

- **Argument Count Validation**: Ensures correct number of arguments
- **Type Checking**: Validates numeric parameters
- **Usage Documentation**: Provides helpful error messages
- **Extensible Registry**: Easy to add custom commands

### Adding Custom Commands

You can extend Radish with custom commands:

```python
from src.validation_handler import ValidationHandler

handler = ValidationHandler()

# Register a custom command
handler.register_command(
    command='CUSTOM',
    min_args=2,
    max_args=3,
    usage='CUSTOM key [value]',
    types=[str, str, str]
)
```

## Event System

Radish provides a sophisticated event system for monitoring and reacting to cache operations.

### Event Architecture

The event system consists of:
1. **Event Registry** - Manages event subscriptions and dispatching
2. **Event Context** - Provides comprehensive operation details
3. **Event Handlers** - User-defined callbacks for specific events

### Basic Event Handling

```python
from src.cache_handler import CacheHandler, CacheEvent, CacheEventContext

# Create the cache handler
cache = CacheHandler()

# Monitor all SET operations
def on_value_set(ctx: CacheEventContext):
    print(f"New value in {ctx.cache_name}: {ctx.key} = {ctx.value}")

cache.on(CacheEvent.SET, on_value_set)
```

### Available Events

- `CacheEvent.GET` - Value retrieval operations
- `CacheEvent.SET` - Value setting operations
- `CacheEvent.DELETE` - Key deletion operations
- `CacheEvent.EXPIRE` - Key expiration events
- `CacheEvent.CLEAR` - Cache clearing operations
- `CacheEvent.CREATE_CACHE` - New cache creation
- `CacheEvent.DELETE_CACHE` - Cache deletion
- `CacheEvent.LIST_PUSH` - List push operations (LPUSH/RPUSH)
- `CacheEvent.LIST_POP` - List pop operations (LPOP/RPOP)

### Event Context

Each event handler receives a `CacheEventContext` with:
- `cache_name`: Name of the cache being operated on
- `key`: Key being accessed/modified
- `value`: New value (for SET events)
- `old_value`: Previous value (for SET/DELETE)
- `event_type`: Type of event
- `timestamp`: When the event occurred

### Event Use Cases

#### 1. Monitoring Cache Access

```python
def log_access(ctx: CacheEventContext):
    print(f"Cache accessed: {ctx.cache_name}.{ctx.key}")
    
# Monitor all GET operations
cache.on(CacheEvent.GET, log_access)
```

#### 2. Cache-Specific Monitoring

```python
def monitor_users(ctx: CacheEventContext):
    print(f"User modified: {ctx.key}")
    print(f"New data: {ctx.value}")
    
# Monitor only the "users" cache
cache.on(CacheEvent.SET, monitor_users, cache_name="users")
```

#### 3. Statistics Collection

```python
stats = {"sets": 0, "gets": 0, "deletes": 0}

def collect_stats(ctx: CacheEventContext):
    if ctx.event_type == CacheEvent.SET:
        stats["sets"] += 1
    elif ctx.event_type == CacheEvent.GET:
        stats["gets"] += 1
    elif ctx.event_type == CacheEvent.DELETE:
        stats["deletes"] += 1

# Monitor multiple events
for event in [CacheEvent.SET, CacheEvent.GET, CacheEvent.DELETE]:
    cache.on(event, collect_stats)
```

#### 4. Expiration Monitoring

```python
def handle_expiry(ctx: CacheEventContext):
    print(f"Key expired: {ctx.cache_name}.{ctx.key}")
    # Perform cleanup or logging
    
cache.on(CacheEvent.EXPIRE, handle_expiry)
```

#### 5. Removing Event Handlers

```python
# Stop monitoring when needed
cache.off(CacheEvent.SET, monitor_users, cache_name="users")
```

### Thread Safety

All event handling methods are thread-safe and can be used safely in concurrent environments. Event handlers are executed synchronously in the thread that triggered the event.

## Command Reference

### Basic Operations

| Command | Syntax | Description |
|---------|--------|-------------|
| `PING` | `PING` | Test server connection |
| `EXIT` | `EXIT` | Close the connection |
| `INSPECT` | `INSPECT` | Show all key-value pairs |

### Key-Value Operations

| Command | Syntax | Description |
|---------|--------|-------------|
| `SET` | `SET key value` | Set a key-value pair |
| `GET` | `GET key` | Get value for a key |
| `DEL` | `DEL key` | Delete a key |
| `EXPIRE` | `EXPIRE key seconds` | Set expiration time for a key |

### List Operations

| Command | Syntax | Description |
|---------|--------|-------------|
| `LPUSH` | `LPUSH key value` | Push value to the start of a list |
| `RPUSH` | `RPUSH key value` | Push value to the end of a list |
| `LPOP` | `LPOP key` | Remove and return the first element |

### Cache Management

| Command | Syntax | Description |
|---------|--------|-------------|
| `CREATECACHE` | `CREATECACHE cache_name` | Create a new cache |
| `DELETECACHE` | `DELETECACHE cache_name` | Delete an existing cache |
| `LISTCACHES` | `LISTCACHES` | List all available caches with sizes |

### Cache Operations

| Command | Syntax | Description |
|---------|--------|-------------|
| `CACHESET` | `CACHESET cache_name key value` | Set a key-value pair in a named cache |
| `CACHEGET` | `CACHEGET cache_name key` | Get a value from a named cache |
| `CACHEDEL` | `CACHEDEL cache_name key` | Delete a key from a named cache |
| `CACHEKEYS` | `CACHEKEYS cache_name` | List all keys in a named cache |
| `CACHEGETALL` | `CACHEGETALL cache_name` | Get all key-value pairs from a cache as JSON |

### Store Management (Advanced)

| Command | Syntax | Description |
|---------|--------|-------------|
| `CREATESTORE` | `CREATESTORE cache_name store_name [ttl]` | Create a new expiring store in a cache |
| `DELETESTORE` | `DELETESTORE cache_name store_name` | Delete a store from a cache |
| `LISTSTORES` | `LISTSTORES cache_name` | List all stores in a cache |

## Tips and Best Practices

### 1. Organizing Data with Named Caches

Use named caches to organize different types of data:

```
CREATECACHE users        # User accounts
CREATECACHE sessions     # User sessions
CREATECACHE products     # Product catalog
CREATECACHE settings     # Application settings
```

### 2. Using Consistent Key Naming

Adopt a consistent naming convention for keys:

```
# Good: Hierarchical naming
user:1:profile
user:1:settings
product:100:details
product:100:inventory

# Also good: Namespace prefixes
usr_1_profile
usr_1_settings
prd_100_details
prd_100_inventory
```

### 3. Setting Appropriate TTLs

Set expiration times for temporary data:

```
# Session tokens (1 hour)
SET session:abc123 "user_data"
EXPIRE session:abc123 3600

# Email verification codes (15 minutes)
SET verify:user@example.com "code123"
EXPIRE verify:user@example.com 900

# Cache data (5 minutes)
SET cache:api:response "data"
EXPIRE cache:api:response 300
```

### 4. Working with JSON Data

Store complex data structures as JSON:

```
# User profile
SET user:1 {"name": "Alice", "email": "alice@example.com", "role": "admin"}

# Product details
CACHESET products item:100 {"name": "Laptop", "price": 1200, "stock": 5}

# Configuration
SET config:app {"debug": true, "version": "1.0.0", "features": ["cache", "events"]}
```

### 5. Bulk Operations with CACHEGETALL

Retrieve all data from a cache efficiently:

```python
import socket
import json

def get_all_users():
    # Connect and send command
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 6379))
    sock.sendall(b'CACHEGETALL users\n')
    
    # Parse JSON response
    response = sock.recv(4096).decode()
    users = json.loads(response)
    return users
```

### 6. Monitoring with Events

Use the event system to track important operations:

```python
# Log all cache modifications
def audit_log(ctx):
    with open('audit.log', 'a') as f:
        f.write(f"{ctx.timestamp}: {ctx.event_type} - {ctx.cache_name}.{ctx.key}\n")

cache.on(CacheEvent.SET, audit_log)
cache.on(CacheEvent.DELETE, audit_log)
```

### 7. Error Handling

Always handle connection errors and invalid responses:

```python
import socket

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 6379))
    sock.sendall(b'GET mykey\n')
    response = sock.recv(1024).decode().strip()
    
    if response == "(nil)":
        print("Key not found")
    else:
        print(f"Value: {response}")
        
except ConnectionRefusedError:
    print("Server is not running")
except Exception as e:
    print(f"Error: {e}")
finally:
    sock.close()
```

### 8. Testing Your Commands

Use the test scripts to verify functionality:

```bash
# Test basic commands
./scripts/test_commands.sh

# Test named caches
./scripts/test_named_cache.sh

# Test HTTP API
./scripts/test_http.sh
```

## Examples and Resources

- **[Named Cache Guide](NAMED_CACHE_GUIDE.md)** - Detailed guide to named caches
- **[HTTP Server Guide](HTTP_SERVER_GUIDE.md)** - REST API documentation
- **Python Examples**: Check the `scripts/` directory for working examples
- **Test Scripts**: Use scripts in `scripts/` to see commands in action

## Troubleshooting

### Server Won't Start

**Problem**: Port already in use
```
OSError: [Errno 98] Address already in use
```

**Solution**: Kill existing process or use a different port
```bash
# Find process using port 6379
lsof -i :6379

# Kill the process
kill -9 <PID>
```

### Connection Refused

**Problem**: Can't connect to server
```
telnet: Unable to connect to remote host: Connection refused
```

**Solution**: Ensure server is running
```bash
python server.py
```

### Key Not Found

**Problem**: Getting `(nil)` for existing key

**Possible causes**:
1. Key has expired (check TTL)
2. Wrong cache (use correct cache name)
3. Typo in key name

### JSON Parsing Errors

**Problem**: JSON data appears malformed

**Solution**: Use proper quoting
```
# Good
SET user:1 {"name": "Alice"}

# Also works with escaped quotes
SET user:1 {\"name\": \"Alice\"}
```

## Next Steps

- Explore the [HTTP API](HTTP_SERVER_GUIDE.md) for REST access
- Learn about [Named Caches](NAMED_CACHE_GUIDE.md) in detail
- Check the [Project Roadmap](TODO.md) for upcoming features
- Run the example scripts in `scripts/` directory
- Contribute to the project on [GitHub](https://github.com/gideonca/radish)
