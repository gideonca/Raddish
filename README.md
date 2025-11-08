# Radish

A lightweight Redis-like in-memory data store implementation in Python. Radish provides a thread-safe key-value store with automatic key expiration and a Redis-compatible command interface.

## Features

- **In-memory key-value store** - Fast data access with automatic expiration (TTL)
- **Named caches** - Organize data into isolated namespaces
- **Thread-safe operations** - Concurrent client support with fine-grained locking
- **Event system** - Monitor and react to cache operations
- **Redis-like commands** - Familiar interface for Redis users
- **HTTP API** - REST access without external dependencies
- **List operations** - LPUSH, RPUSH, LPOP support
- **No dependencies** - Pure Python using only the standard library

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete guide to using Radish with examples and best practices
- **[Named Cache Guide](docs/NAMED_CACHE_GUIDE.md)** - Comprehensive guide to using named caches for organizing data
- **[HTTP Server Guide](docs/HTTP_SERVER_GUIDE.md)** - Complete HTTP API documentation with examples
- **[Project Roadmap](docs/TODO.md)** - Planned features and development tasks

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gideonca/radish.git
cd radish
```

2. Start the server:
```bash
python server.py
```

3. Connect using telnet:
```bash
telnet localhost 6379
```

### Basic Usage

```
> PING
PONG

> SET mykey "Hello World"
OK

> GET mykey
Hello World

> EXPIRE mykey 60
OK

> EXIT
Goodbye!
```

For detailed usage instructions, see the **[User Guide](docs/USER_GUIDE.md)**.

### HTTP API

Start the HTTP server for REST API access:

```bash
python http_server.py
```

See the **[HTTP Server Guide](docs/HTTP_SERVER_GUIDE.md)** for complete API documentation.

## Command Overview

### Basic Commands
- `PING`, `SET`, `GET`, `DEL`, `EXPIRE`, `INSPECT`

### List Operations
- `LPUSH`, `RPUSH`, `LPOP`

### Named Caches
- `CREATECACHE`, `DELETECACHE`, `LISTCACHES`
- `CACHESET`, `CACHEGET`, `CACHEDEL`, `CACHEKEYS`, `CACHEGETALL`

### Advanced Features
- `CREATESTORE`, `DELETESTORE`, `LISTSTORES` (Expiring stores)

For complete command reference and examples, see the **[User Guide](docs/USER_GUIDE.md)**.

## Development

Run the test suite:
```bash
python3 -m unittest discover tests
```

## Implementation Details

### Architecture

Radish is built on a robust, modular architecture with clear separation of concerns:

- **Validation Layer** (`validation_handler.py`)
  - Registry-based command validation
  - Argument count and type checking
  - Extensible command specification system
  - Built-in usage documentation

- **Command Processing** (`command_handler.py`)
  - Command routing and execution
  - Error handling and response formatting
  - Integration with validation and cache systems
  - Support for custom command registration

- **Cache Management** (`cache_handler.py`)
  - Event-driven architecture
  - Thread-safe operations
  - Comprehensive event system
  - Support for multiple cache instances

- **Data Store** (`expiring_store.py`)
  - TTL-based key expiration
  - Automatic background cleanup
  - Thread-safe value storage
  - Support for various data types

### Technical Features

- Written in pure Python with no external dependencies
- Uses threading for concurrent client handling
- Thread-safe operations using fine-grained locks
- Event-driven architecture for extensibility
- Redis-compatible network protocol
- Automatic background maintenance tasks

## Project Structure

```
radish/
├── server.py                          # Main server implementation
├── src/
│   ├── validation_handler.py          # Command validation and registry
│   ├── command_handler.py             # Command processing
│   ├── cache_handler.py               # Cache management and events
│   ├── expiring_store.py              # Key-value store with TTL and named caches
│   ├── event_handler.py               # Event system
│   ├── persistence_handler.py         # Data persistence
│   └── stats_handler.py               # Statistics tracking
├── tests/
│   ├── test_validation_handler.py     # Validation system tests
│   ├── test_command_handler.py        # Command handler tests
│   ├── test_cache_handler.py          # Cache handler tests
│   ├── test_enhanced_cache_handler.py # Extended cache features
│   ├── test_enhanced_features.py      # Additional functionality
│   └── test_expiration_manager.py     # TTL and expiration tests
├── docs/
│   ├── NAMED_CACHE_GUIDE.md           # Named cache system guide
│   ├── HTTP_SERVER_GUIDE.md           # HTTP API documentation
│   └── TODO.md                        # Project roadmap and tasks
├── scripts/
│   ├── test_commands.sh               # Test script for common commands
│   ├── test_named_cache.sh            # Test script for named caches
│   ├── test_http.sh                   # Test script for HTTP API
│   ├── test_cachegetall.py            # Test script for CACHEGETALL
│   ├── example_named_cache.py         # Python example for named caches
│   └── example_http_client.py         # Python HTTP client example
├── README.md                          # Project documentation
├── requirements.txt                   # Project dependencies
├── server.py                          # Main TCP server (port 6379)
└── http_server.py                     # HTTP API server (port 8000)
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