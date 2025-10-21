# Radish

A lightweight Redis-like in-memory data store implementation in Python. Radish provides a thread-safe key-value store with automatic key expiration and a Redis-compatible command interface.

## Features

- In-memory key-value store
- Automatic key expiration (TTL support)
- Thread-safe operations
- Background cleanup of expired keys
- Redis-like command interface
- TCP socket server for network access
- Concurrent client support

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gideonca/radish.git
cd Radish
```

2. (Optional) Create and activate a virtual environment:
* note: there are no external packages in this project as of now
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Running

1. Start the server:
```bash
python server.py
```

2. Connect using telnet in another terminal:
```bash
telnet localhost 6379
```

### Basic Usage

The following examples show how to interact with Radish using telnet:

#### Basic Operations
```
> PING
PONG

# Simple key-value operations
> SET mykey "Hello World"
OK
> GET mykey
Hello World
> DEL mykey
OK

# Working with JSON data
> SET users:1 {"name": "John", "age": 30}
OK
> GET users:1
{"name": "John", "age": 30}

# Setting expiration time (in seconds)
> SET users:2 {"name": "Jane"}
OK
> EXPIRE users:2 60
OK
```

#### Working with Lists
```
# Adding elements to a list
> RPUSH mylist "first"
OK
> RPUSH mylist "second"
OK
> LPUSH mylist "start"
OK

# Removing elements
> LPOP mylist
start
```

#### Tips for JSON Data
When working with JSON data, you can include spaces in your JSON strings - the server will handle them correctly:
```
# All of these formats work:
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
```

#### Available Commands
- `PING` - Test server connection
- `SET key value` - Set a key-value pair
- `GET key` - Get value for a key
- `DEL key` - Delete a key
- `EXPIRE key seconds` - Set expiration time for a key
- `LPUSH key value` - Push value to the start of a list
- `RPUSH key value` - Push value to the end of a list
- `LPOP key` - Remove and return the first element of a list
- `EXIT` - Close the connection

To exit the telnet session:
1. Type `EXIT` command, or
2. Press `Ctrl+]` and then type `quit`

### Event System

Radish provides a powerful event system that lets you monitor and react to cache operations. Here's how to use it:

#### Basic Event Handling
```python
from src.cache_handler import CacheHandler, CacheEvent, CacheEventContext

# Create the cache handler
cache = CacheHandler()

# Monitor all SET operations
def on_value_set(ctx: CacheEventContext):
    print(f"New value in {ctx.cache_name}: {ctx.key} = {ctx.value}")

cache.on(CacheEvent.SET, on_value_set)
```

#### Available Events
- `CacheEvent.GET` - Triggered when retrieving a value
- `CacheEvent.SET` - Triggered when setting a value
- `CacheEvent.DELETE` - Triggered when deleting a key
- `CacheEvent.EXPIRE` - Triggered when a key expires
- `CacheEvent.CLEAR` - Triggered when clearing a cache
- `CacheEvent.CREATE_CACHE` - Triggered when creating a new cache
- `CacheEvent.DELETE_CACHE` - Triggered when deleting a cache

#### Event Context
Each event handler receives a `CacheEventContext` with:
- `cache_name`: Name of the cache being operated on
- `key`: Key being accessed/modified
- `value`: New value (for SET events)
- `old_value`: Previous value (for SET/DELETE)
- `event_type`: Type of event
- `timestamp`: When the event occurred

#### Example Use Cases

1. **Monitoring Cache Access**
```python
def log_access(ctx: CacheEventContext):
    print(f"Cache accessed: {ctx.cache_name}.{ctx.key}")
    
# Monitor all GET operations
cache.on(CacheEvent.GET, log_access)
```

2. **Cache-Specific Monitoring**
```python
def monitor_users(ctx: CacheEventContext):
    print(f"User modified: {ctx.key}")
    print(f"New data: {ctx.value}")
    
# Monitor only the "users" cache
cache.on(CacheEvent.SET, monitor_users, cache_name="users")
```

3. **Statistics Collection**
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

4. **Expiration Monitoring**
```python
def handle_expiry(ctx: CacheEventContext):
    print(f"Key expired: {ctx.cache_name}.{ctx.key}")
    # Perform cleanup or logging
    
cache.on(CacheEvent.EXPIRE, handle_expiry)
```

5. **Removing Event Handlers**
```python
# Stop monitoring when needed
cache.off(CacheEvent.SET, monitor_users, cache_name="users")
```

#### Thread Safety
All event handling methods are thread-safe and can be used safely in concurrent environments. Event handlers are executed synchronously in the thread that triggered the event.
> GET mykey
Hello World
> EXPIRE mykey 10
OK
> EXIT
Goodbye!
```

## Development

Run the test suite:
```bash
python3 -m unittest discover tests
```

## Implementation Details

- Written in pure Python
- Uses threading for concurrency
- Thread-safe operations using locks
- Automatic background cleanup of expired keys
- Network protocol similar to Redis

## Project Structure

```
radish/
├── server.py                # Main server implementation
├── src/
│   ├── validator.py         # Command validation
│   ├── command_handler.py   # Command processing
│   ├── cache_handler.py     # Cache management and events
│   └── expiring_store.py    # Key-value store with TTL
├── tests/
│   ├── test_server.py           # Server tests
│   ├── test_expiration.py       # Expiration tests
│   ├── test_rpush.py           # RPUSH command tests
│   ├── test_command_handler.py  # Command handler tests
│   └── test_cache_handler.py    # Cache handler tests
├── README.md                # Project documentation
├── requirements.txt         # Project dependencies
└── venv/                   # Virtual environment (optional)
```

## Use Cases

1. **Development and Testing**
   - Local Redis replacement for development
   - Testing Redis-dependent applications
   - Learning Redis commands and behavior

2. **Educational**
   - Understanding key-value stores
   - Learning about concurrent programming
   - Studying Redis internals

3. **Prototyping**
   - Quick proof-of-concepts
   - System architecture exploration
   - Simple caching implementations