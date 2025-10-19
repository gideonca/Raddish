# Reddish

A lightweight Redis-like in-memory data store implementation in Python. Reddish provides a thread-safe key-value store with automatic key expiration and a Redis-compatible command interface.

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
git clone https://github.com/gideonca/reddish.git
cd reddish
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

The following examples show how to interact with Reddish using telnet:

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

Reddish provides a powerful event system that lets you monitor and react to cache operations. Here's how to use it:

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
reddish/
├── server.py              # Main server implementation
├── src/
│   ├── validator.py       # Command validation
│   ├── command_handler.py # Command processing
│   └── expiring_store.py  # Key-value store with TTL
└── tests/                 # Unit tests
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

## Current Features and Roadmap

# TODO List
# Introduction
  - [x] Bind to a port
  - [x] Respond to PING (PING)
  - [x] Respond to multiple PINGs 
  - [x] Handle concurrent clients (event loop)
  - [x] Implement the ECHO command (ECHO)
  - [x] Implement the SET & GET commands (SET & GET)
  - [x] Expiry (Add PX argument to SET command)

# Lists
  - [x] Create a list (RPUSH -> Return num elements as RESP int)
  - [x] Append an element (existing list support for RPUSH)
  - [ ] Append multiple elements 
  - [ ] List elements (positive indexes) (LRANGE w/ start and end index)
  - [ ] List elements (negative indexes) (See above, get abs val)
  - [x] Prepend elements (LPUSH -> Inserts right to left rather than left to right)
  - [ ] Query list length (LLEN)
  - [x] Remove an element (LPOP)
  - [ ] Remove multiple elements
  - [ ] Blocking retrieval (BLPOP)
  - [ ] Blocking retrieval with timeout (BLPOP with PX)

# Streams
  - [ ] The TYPE command (TYPE)
  - [ ] Create a stream (XADD - id's are random seq num - current ms)
  - [ ] Validating entry IDs (Verify new id's are greater than the stream top item)
  - [ ] Partially auto-generated IDs 
  - [ ] Fully auto-generated IDs
  - [ ] Query entries from stream (XRANGE - return RESP Array of entries)
  - [ ] Query with - (Return entries from beginning of stream to given id)
  - [ ] Query with + (Retrieve entries from given id to end of stream)
  - [ ] Query single stream using XREAD
  - [ ] Query multiple streams using XREAD
  - [ ] Blocking reads
  - [ ] Blocking reads without timeout
  - [ ] Blocking reads using $

# Transactions
  - [ ] The INCR command (1/3)
  - [ ] The INCR command (2/3)
  - [ ] The INCR command (3/3)
  - [ ] The MULTI command
  - [ ] The EXEC command
  - [ ] Empty transaction
  - [ ] Queueing commands
  - [ ] Executing a transaction
  - [ ] The DISCARD command
  - [ ] Failures within transactions
  - [ ] Multiple transactions

# Replication
  - [ ] Configure listening port
  - [ ] The INFO command
  - [ ] The INFO command on a replica
  - [ ] Initial replication ID and offset
  - [ ] Send handshake (1/3)
  - [ ] Send handshake (2/3)
  - [ ] Send handshake (3/3)
  - [ ] Receive handshake (1/2)
  - [ ] Receive handshake (2/2)
  - [ ] Empty RDB transfer
  - [ ] Single-replica propagation
  - [ ] Multi-replica propagation
  - [ ] Command processing
  - [ ] ACKs with no commands
  - [ ] ACKs with commands
  - [ ] WAIT with no replicas
  - [ ] WAIT with no commands
  - [ ] WAIT with multiple commands

# RDB Persistence
  - [ ] RDB file config
  - [ ] Read a key
  - [ ] Read a string value
  - [ ] Read multiple keys
  - [ ] Read multiple string values
  - [ ] Read value with expiry

# Pub/Sub
  - [ ] Subscribe to a channel
  - [ ] Subscribe to multiple channels
  - [ ] Enter subscribed mode
  - [ ] PING in subscribed mode
  - [ ] Publish a message
  - [ ] Deliver messages
  - [ ] Unsubscribe

# Sorted Sets
  - [ ] Create a sorted set
  - [ ] Add members
  - [ ] Retrieve member rank
  - [ ] List sorted set members
  - [ ] ZRANGE with negative indexes
  - [ ] Count sorted set members
  - [ ] Retrieve member score
  - [ ] Remove a member