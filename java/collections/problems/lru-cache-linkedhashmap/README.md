# LRU Cache with LinkedHashMap

## Problem Statement

Design and implement an LRU (Least Recently Used) cache using `LinkedHashMap` that evicts the least recently accessed entry when the cache reaches its maximum capacity.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Get operation**: Return value for key; move accessed key to most recent position.
- **Put operation**: Insert or update key-value pair; evict LRU entry if at capacity.
- **Capacity limit**: Fixed maximum size; automatic eviction on overflow.
- **Access order**: Track access order (get and put both update recency).
- **O(1) operations**: Both get and put must be O(1) time complexity.

### Non-Functional Requirements
- **Performance**: O(1) for get and put operations.
- **Thread safety**: Optional concurrent version using ConcurrentHashMap-based approach.
- **Memory efficiency**: Minimal overhead per entry.

## Key Design Decisions
- **LinkedHashMap**: Extends HashMap with a doubly-linked list for access order.
- **Access order mode**: Constructor parameter `accessOrder = true` reorders on access.
- **removeEldestEntry**: Override to return `true` when size > capacity, triggering eviction.
- **Staff insight**: LinkedHashMap is the simplest way to implement LRU cache in Java with O(1) operations.

## Staff-Level Design Considerations

### LinkedHashMap Implementation
```java
class LRUCache<K,V> extends LinkedHashMap<K,V> {
    private final int capacity;
    LRUCache(int capacity) {
        super(capacity, 0.75f, true);  // accessOrder = true
        this.capacity = capacity;
    }
    @Override
    protected boolean removeEldestEntry(Map.Entry<K,V> eldest) {
        return size() > capacity;
    }
}
```
- **Staff insight**: The load factor is set to 0.75f but doesn't matter much since we override `removeEldestEntry`. The accessOrder parameter is the key — it enables LRU behavior.

### Production-Grade Alternatives
- **Caffeine**: Best-performing Java cache; supports LRU, LFU, windowed TTL, and more.
- **Guava Cache**: Feature-rich but no longer actively maintained; migrate to Caffeine.
- **Custom implementation**: For simple LRU, LinkedHashMap suffices; for production, use Caffeine.
- **Staff insight**: Caffeine uses Window TinyLFU eviction policy, which has better hit rates than pure LRU. It also supports async loading, automatic refresh, and size-based eviction.

### Thread-Safe LRU Cache
- **Collections.synchronizedMap**: Wraps LinkedHashMap but has poor concurrent performance.
- **ConcurrentHashMap**: Doesn't support LRU eviction natively.
- **Custom approach**: Use ConcurrentHashMap + separate LRU tracking with striped locks.
- **Staff insight**: For thread-safe LRU cache in production, use Caffeine. It's designed for high concurrency with segment-level locking and lock-free reads.

### Common Pitfalls
- **Forgetting accessOrder**: Without `accessOrder = true`, LinkedHashMap uses insertion order, not access order.
- **Not overriding removeEldestEntry**: Cache grows unbounded without eviction.
- **Concurrent access**: LinkedHashMap is not thread-safe; wrap or use concurrent alternative.
- **Staff insight**: LinkedHashMap-based LRU is great for interviews and simple use cases. For production systems with high concurrency, always prefer Caffeine.
