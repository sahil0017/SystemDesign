# Thread-Safe Cache with TTL (Concurrency)

## Problem Statement

Design a thread-safe in-memory cache with Time-To-Live (TTL) expiration that supports concurrent reads and writes. The cache should automatically evict expired entries and provide O(1) get/put operations.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **get(key)**: Return value if key exists and not expired; return null otherwise.
- **put(key, value, ttl)**: Insert or update key-value pair with TTL in milliseconds.
- **remove(key)**: Remove a key from the cache.
- **TTL expiration**: Entries expire after the specified TTL.
- **Lazy expiration**: Check TTL on get/put operations.
- **Eager expiration**: Background thread periodically removes expired entries.
- **Size limit**: Maximum cache size; evict LRU entry when full.

### Non-Functional Requirements
- **Thread safety**: Support concurrent reads and writes without data corruption.
- **Performance**: O(1) get/put operations.
- **No stale reads**: Never return an expired value.
- **Memory efficiency**: Expired entries are garbage collected promptly.

## Key Design Decisions
- **ConcurrentHashMap**: Thread-safe storage with segment-level locking.
- **DelayQueue**: Tracks expiration times for eager cleanup.
- **ReadWriteLock**: Concurrent reads with exclusive writes.
- **Lazy + eager cleanup**: Check TTL on access + background cleanup thread.

## Class Diagram

```
┌──────────────────┐     ┌──────────────────┐
│  TTLCache        │────►│  CacheEntry      │
├──────────────────┤     ├──────────────────┤
│ - map: ConcurrentHashMap │ - key        │
│ - expiryQueue    │     │ - value          │
│ - maxSize        │     │ - expiryTime     │
│ - cleanupThread  │     │ - creationTime   │
├──────────────────┤     └──────────────────┘
│ + get(key)       │
│ + put(key, val, ttl)│
│ + remove(key)    │
│ + cleanup()      │
└──────────────────┘
```

## Staff-Level Design Considerations

### Lazy vs Eager Expiration
- **Lazy**: Check TTL on `get()` — simple but expired entries linger until accessed.
- **Eager**: Background thread removes expired entries — uses CPU but keeps cache clean.
- **Staff insight**: Use both. Lazy expiration ensures no stale reads. Eager expiration prevents memory bloat from unused expired entries.

### DelayQueue for Expiration
- **Ordering**: `DelayQueue` orders entries by expiration time; poll returns the next expired entry.
- **Staff insight**: `DelayQueue` is efficient for eager cleanup — O(log n) to add, O(log n) to poll. Don't scan all entries to find expired ones — that's O(n).

### ConcurrentHashMap vs Synchronized Map
- **Segment locking**: `ConcurrentHashMap` uses bucket-level locking, not global locking.
- **Staff insight**: `ConcurrentHashMap` allows concurrent reads and writes to different buckets. A `synchronized` wrapper blocks all operations on any write — terrible throughput under contention.

### Caffeine as Production Alternative
- **Window-based LRU**: Caffeine uses a window-based admission and loading strategy that outperforms pure LRU.
- **Staff insight**: Don't roll your own cache in production. Use Caffeine — it handles TTL, LRU, async reload, and eviction listeners with better performance than any hand-rolled solution.
