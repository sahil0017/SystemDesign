# Caffeine Cache Design

## Problem Statement

Design a high-performance in-memory caching layer using Caffeine that supports LRU/LFU eviction, TTL-based expiration, async loading, and automatic refresh for production-grade caching.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Cache loading**: Synchronous and asynchronous value loading with `CacheLoader`.
- **Eviction policies**: LRU (Least Recently Used), LFU (Least Frequently Used), size-based.
- **Expiration**: Time-based (TTL) and access-based (TTI) expiration.
- **Refresh**: Automatic refresh of stale values without blocking reads.
- **Statistics**: Hit/miss rate, load success/failure, eviction count.

### Non-Functional Requirements
- **Performance**: Best-in-class throughput and latency for in-memory caching.
- **Thread safety**: Concurrent access from multiple threads.
- **Memory efficiency**: Bounded memory usage with proper eviction.

## Key Design Decisions
- **Caffeine**: Best-performing Java cache; uses Window TinyLFU admission policy.
- **Builder API**: Fluent configuration for cache policies.
- **Async cache**: `AsyncCache` for non-blocking cache loading.
- **Segmented locking**: Internal lock striping for high concurrency.

## Staff-Level Design Considerations

### Caffeine vs Alternatives
- **Caffeine**: Window TinyLFU + LRU; best hit rate and throughput. Recommended for all new projects.
- **Guava Cache**: Similar API but no longer actively maintained; migrate to Caffeine.
- **LinkedHashMap**: Simple LRU but not thread-safe and no TTL; good for interviews only.
- **ConcurrentHashMap**: No eviction; manual TTL management; not a cache.
- **Staff insight**: Caffeine's Window TinyLFU admission policy tracks access frequency with minimal overhead. It admits frequently accessed items and evicts rarely accessed ones, achieving near-optimal hit rates. This is superior to pure LRU for most workloads.

### Configuration Best Practices
```java
Cache<Key, Value> cache = Caffeine.newBuilder()
    .maximumSize(10_000)              // Max entries
    .expireAfterWrite(10, TimeUnit.MINUTES)  // TTL
    .expireAfterAccess(5, TimeUnit.MINUTES)  // Access-based expiry
    .recordStats()                    // Enable statistics
    .refreshAfterWrite(5, TimeUnit.MINUTES)  // Auto-refresh
    .removalListener((key, value, cause) ->  // Eviction callback
        log.info("Evicted: {} due to {}", key, cause))
    .build(key -> loadFromDatabase(key));    // CacheLoader
```
- **Staff insight**: Always set `maximumSize` to prevent unbounded growth. Use `expireAfterWrite` for data freshness and `expireAfterAccess` for memory efficiency. Enable `recordStats()` in development to tune cache size and TTL.

### Async Cache Pattern
```java
AsyncCache<Key, Value> cache = Caffeine.newBuilder()
    .maximumSize(10_000)
    .buildAsync(key -> CompletableFuture.supplyAsync(() -> load(key), executor));
```
- **Staff insight**: Use `AsyncCache` when cache loading involves I/O (DB, HTTP). It doesn't block the calling thread while loading. Always provide a custom executor — don't use the common ForkJoinPool for IO-bound tasks.

### Common Pitfalls
- **No max size**: Cache grows unbounded; causes OOM. Always set `maximumSize`.
- **Synchronous loading**: Blocks calling thread during cache miss. Use `AsyncCache` for IO-bound loads.
- **Cache stampede**: Multiple threads load the same key simultaneously on cache miss. Use `get(key, loadingFunction)` which serializes loading per key.
- **Staff insight**: Cache stampede (thundering herd) is the most common performance issue. When a hot key expires, all concurrent requests try to reload it. Caffeine's `get(key, function)` method ensures only one thread loads the value while others wait for the result.
