# Cache with Expiry

## Problem Statement

Design a thread-safe in-memory cache with TTL (Time-To-Live) expiry support.

**Reference**: AlgoMaster

## Requirements
- **put(key, value, ttl)**: Store with expiry time.
- **get(key)**: Return value if not expired; remove if expired.
- **Background cleanup**: Remove expired entries periodically.
- **Thread safety**: Concurrent reads and writes.

## Key Design Decisions
- **ConcurrentHashMap**: Thread-safe storage.
- **Delayed queue**: `DelayQueue` for expiry notification.
- **Lazy + eager cleanup**: Check expiry on get() + background thread for cleanup.

## Staff-Level Design Considerations
- **Staff insight**: Pure lazy cleanup leaves expired entries until accessed. Pure eager cleanup wastes CPU. Hybrid approach: lazy check on get() + background thread that runs every N seconds to clean up. This is what Caffeine does.
