## Current Features and Roadmap

# TODO List
# Basic
  - [x] Bind to a port
  - [x] Respond to PING (PING)
  - [x] Respond to multiple PINGs 
  - [x] Handle concurrent clients (event loop)
  - [x] Implement the ECHO command (ECHO)
  - [x] Implement the SET & GET commands (SET & GET)
  - [x] Expiry (Add PX argument to SET command)
  - [ ] Replication of cache
  - [ ] Implementation of LRU

# Lists
  - [x] Create a list (RPUSH -> Return num elements as RESP int)
  - [x] Append an element (existing list support for RPUSH)
  - [X] Prepend element to list (LPUSH)
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