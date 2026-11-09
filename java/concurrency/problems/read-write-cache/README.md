# Read-Write Cache

## Problem Statement

Design a high-performance concurrent cache that supports multiple concurrent readers and exclusive writers, using optimistic read strategies and efficient write coordination for maximum throughput.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Concurrent reads**: Multiple threads can read simultaneously without blocking.
- **Exclusive writes**: Only one writer at a time; readers may be blocked during write.
- **Optimistic reads**: Lock-free reads that retry if a write occurs concurrently.
- **Cache eviction**: LRU/LFU eviction when cache reaches maximum size.
- **TTL support**: Time-to-live expiration for cache entries.

### Non-Functional Requirements
- **Read throughput**: Lock-free reads with no contention.
- **Write safety**: Writers see a consistent view of the cache.
- **Scalability**: Performance scales with number of reader threads.

## Key Design Decisions
- **StampedLock**: Java 8+ lock for optimistic reads; best read performance.
- **Segmented cache**: Multiple segments to reduce write contention.
- **Copy-on-write**: For simple caches, copy the entire map on write.
- **Caffeine**: Production-grade cache with segmented locking.

## Staff-Level Design Considerations

### StampedLock for Read-Write Cache
```java
class StampedCache<K,V> {
    private final StampedLock lock = new StampedLock();
    private final Map<K,V> map = new HashMap<>();
    
    public V get(K key) {
        long stamp = lock.tryOptimisticRead();
        V value = map.get(key);
        if (!lock.validate(stamp)) {
            stamp = lock.readLock();
            try {
                value = map.get(key);
            } finally {
                lock.unlockRead(stamp);
            }
        }
        return value;
    }
    
    public void put(K key, V value) {
        long stamp = lock.writeLock();
        try {
            map.put(key, value);
        } finally {
            lock.unlockWrite(stamp);
        }
    }
}
```
- **Staff insight**: `StampedLock`'s optimistic read is the fastest read strategy. It reads without acquiring any lock, then validates that no write occurred during the read. If a write did occur, it falls back to a read lock. For read-heavy workloads (>90% reads), this is significantly faster than ReadWriteLock.

### StampedLock vs ReadWriteLock
- **StampedLock**: Optimistic reads; non-reentrant; no condition support; best read performance.
- **ReadWriteLock**: Pessimistic reads; reentrant; condition support; good balance.
- **synchronized**: Simple; JVM optimizes well for uncontended case; good for low contention.
- **Staff insight**: Use StampedLock when reads vastly outnumber writes and you don't need reentrancy. Use ReadWriteLock when you need reentrancy or condition variables. Use synchronized for simple cases where contention is low — the JVM optimizes it aggressively.

### Segmented Cache Design
- **Segments**: Divide the cache into N segments (e.g., 16), each with its own lock.
- **Hash routing**: Route key to segment using `hash(key) % numSegments`.
- **Per-segment eviction**: Each segment tracks its own LRU order.
- **Staff insight**: Segmented caching is how ConcurrentHashMap achieves high concurrency. Each segment can be written independently, so N segments allow N concurrent writers. The trade-off is that global operations (size, clear) require locking all segments.

### Common Pitfalls
- **Write starvation**: Too many readers can starve writers. Use fair mode or StampedLock.
- **Long read operations**: Holding a read lock during I/O blocks all writers.
- **Stamp misuse**: Forgetting to unlock the stamp causes permanent lock.
- **Staff insight**: Always use try-finally when working with StampedLock to ensure the stamp is unlocked. Unlike ReadWriteLock, StampedLock doesn't track which thread holds the lock — forgetting to unlock permanently blocks all writers.
