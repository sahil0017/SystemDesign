# Caching Strategies

## Trade-off Overview

Cache-aside (lazy loading), write-through, and write-back are the three primary caching strategies, each with different trade-offs in complexity, consistency, and performance.

## Cache-Aside (Lazy Loading)
- **Pattern**: App checks cache → miss → load from DB → write to cache.
- **Pros**: Simple, only caches accessed data, no write overhead.
- **Cons**: First request is slow (cache miss), stale data possible.
- **Use when**: Read-heavy workloads, most common strategy.

## Write-Through
- **Pattern**: App writes to cache and DB simultaneously.
- **Pros**: Cache always fresh, simple reads.
- **Cons**: Every write has cache overhead, writes slower.
- **Use when**: Data must be fresh on every read.

## Write-Back (Write-Behind)
- **Pattern**: App writes to cache only; async batch write to DB.
- **Pros**: Fastest writes, reduced DB writes.
- **Cons**: Data loss on cache failure, complex implementation.
- **Use when**: Write-heavy workloads, some data loss acceptable.

## Staff-Level Insight

> "Cache-aside for 90% of use cases. Write-through when freshness matters. Write-back only for counters."

- **Staff insight**: Use **cache-aside with TTL** for most data. Use **write-through** for user profiles and session data where freshness matters. Use **write-back** only for counters and metrics where occasional data loss is acceptable. Always set **TTL** on cached data — infinite TTL means stale data forever. Use **cache stampede protection** (mutex on cache miss) to prevent thundering herd.
