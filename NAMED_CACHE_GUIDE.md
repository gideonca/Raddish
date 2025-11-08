# Named Cache System - Quick Guide

## Overview
The named cache system allows you to create multiple isolated namespaces (caches) within the server. Each cache can store its own set of key-value pairs, making it easy to organize and manage different types of data.

## Use Cases
- **User Sessions**: Store session data separately from other data
- **Product Catalog**: Keep product information in a dedicated cache
- **Temporary Data**: Create caches for different types of temporary storage
- **Multi-tenancy**: Separate data for different clients or applications

## Commands

### Cache Management

#### CREATECACHE
Create a new named cache.
```
CREATECACHE cache_name
```
**Example:**
```
CREATECACHE users
Response: OK
```

#### DELETECACHE
Delete a named cache and all its contents.
```
DELETECACHE cache_name
```
**Example:**
```
DELETECACHE users
Response: OK
```

#### LISTCACHES
List all available caches with their sizes.
```
LISTCACHES
```
**Example:**
```
LISTCACHES
Response:
Available caches:
- users (3 items)
- products (5 items)
- sessions (10 items)
```

### Cache Operations

#### CACHESET
Set a key-value pair in a specific cache.
```
CACHESET cache_name key value
```
**Example:**
```
CACHESET users user123 john@example.com
Response: OK
```

#### CACHEGET
Get a value from a specific cache.
```
CACHEGET cache_name key
```
**Example:**
```
CACHEGET users user123
Response: john@example.com
```

#### CACHEDEL
Delete a key from a specific cache.
```
CACHEDEL cache_name key
```
**Example:**
```
CACHEDEL users user123
Response: OK
```

#### CACHEKEYS
List all keys in a specific cache.
```
CACHEKEYS cache_name
```
**Example:**
```
CACHEKEYS users
Response:
user123
user456
user789
```

#### CACHEGETALL
Get all key-value pairs from a cache as JSON.
```
CACHEGETALL cache_name
```
**Example:**
```
CACHEGETALL users
Response:
{
  "user123": "john@example.com",
  "user456": "jane@example.com",
  "user789": "bob@example.com"
}
```

## Example Workflow

```bash
# 1. Create caches for different purposes
CREATECACHE users
CREATECACHE products
CREATECACHE sessions

# 2. Store data in the users cache
CACHESET users user:1 john@example.com
CACHESET users user:2 jane@example.com
CACHESET users user:3 bob@example.com

# 3. Store data in the products cache
CACHESET products prod:100 Laptop
CACHESET products prod:101 Mouse

# 4. Retrieve data from a specific cache
CACHEGET users user:1
# Response: john@example.com

# 5. List all keys in the users cache
CACHEKEYS users
# Response:
# user:1
# user:2
# user:3

# 6. Check all caches and their sizes
LISTCACHES
# Response:
# Available caches:
# - users (3 items)
# - products (2 items)
# - sessions (0 items)

# 7. Get all data from a cache as JSON
CACHEGETALL users
# Response:
# {
#   "user:1": "john@example.com",
#   "user:2": "jane@example.com",
#   "user:3": "bob@example.com"
# }

# 8. Delete a key from a cache
CACHEDEL users user:2

# 9. Delete an entire cache
DELETECACHE sessions
```

## Benefits

1. **Isolation**: Keep different types of data separate
2. **Organization**: Easy to manage related data together
3. **Bulk Operations**: Delete all data in a cache at once
4. **Clarity**: Named caches make code more readable
5. **Flexibility**: Each cache is independent

## Implementation Details

- Each cache is a dictionary stored in the main ExpiringStore
- Cache operations are thread-safe
- Caches persist until explicitly deleted
- Keys within a cache must be unique within that cache only
- The same key name can exist in different caches without conflict

## Running the Examples

### Bash Example
```bash
./test_named_cache.sh
```

### Python Example
```bash
python example_named_cache.py
```

## Error Handling

- Creating a cache that already exists: Returns error message
- Accessing a non-existent cache: Returns error message
- Deleting a key that doesn't exist: Returns error message
- Getting a value that doesn't exist: Returns 'NULL'
