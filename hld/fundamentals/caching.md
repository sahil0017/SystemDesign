# Caching

## Overview

Caching stores frequently accessed data in fast storage to reduce latency, decrease backend load, and improve throughput. For staff engineers, caching is a **double-edged sword**: it dramatically improves performance but introduces complexity around consistency, invalidation, and failure modes.

## Cache Types

### By Location (Multi-Tier Caching)

| Tier | Location | Latency | Capacity | Use Case |
|------|----------|---------|----------|----------|
| **L1: Client** | Browser, mobile app | 0ms (local) | Limited | Static assets, API responses |
| **L2: Edge/CDN** | Cloudflare, CloudFront | 10-50ms | Massive | Static content, cached API responses |
| **L3: Application** | Redis, Memcached, Caffeine | 0.1-5ms | GB-TB | Session data, hot records, computed results |
| **L4: Database** | Buffer pool, query cache | 1-10ms | GB | Frequently queried rows |

- **Staff insight**: Multi-tier caching reduces origin load by 90%+. Each tier should have independent TTLs and invalidation strategies. Monitor **cache hit rates per tier** — L3 should be >80%, L2 >90%.

### By Strategy

| Strategy | How It Works | Pros | Cons | Best For |
|----------|-------------|------|------|----------|
| **Cache-Aside (Lazy)** | App checks cache; on miss, loads from DB and caches | Simple, cache contains only requested data | First request slow, possible stale data | Read-heavy workloads |
| **Write-Through** | Write to cache and DB simultaneously | Consistent reads, no stale data | Higher write latency, cache writes on every update | Write-critical data |
| **Write-Behind (Async)** | Write to cache, async batch write to DB | Fast writes, high throughput | Data loss risk on crash, complex | Non-critical writes, counters |
| **Refresh-Ahead** | Pre-load data before TTL expires | No cache miss latency | Wastes bandwidth if data not accessed | Predictable access patterns |

- **Staff insight**: **Cache-Aside** is the default choice for most systems. Use **Write-Through** only when read consistency is critical. Avoid **Write-Behind** for financial data.

## Cache Invalidation Strategies

### TTL-Based
- **Fixed TTL**: All keys expire after N seconds (e.g., 300s for user profiles)
- **Randomized TTL**: TTL ± random jitter to prevent thundering herd (e.g., 300s ± 30s)
- **Staff insight**: Always add jitter to TTLs. Without it, keys expire simultaneously causing **cache stampede**.

### Eviction Policies
- **LRU (Least Recently Used)**: Evict least recently accessed — best for temporal locality
- **LFU (Least Frequently Used)**: Evict least frequently accessed — best for skewed access patterns
- **FIFO (First In, First Out)**: Simple, predictable, ignores access patterns
- **TTL + LRU hybrid**: Expire by age first, then evict by recency — most common in production

### Event-Driven Invalidation
- **Pub/Sub**: On write, publish invalidation event; subscribers purge cache
- **Webhook**: External system notifies cache to invalidate specific keys
- **CDC**: Database change data capture triggers cache updates
- **Staff insight**: Event-driven invalidation provides near-real-time consistency but adds complexity. Use **TTL as a safety net** — even with event invalidation, keys should have max TTL.

## Cache Problems & Solutions

### Cache Penetration
- **Problem**: Requests for non-existent keys bypass cache and hit DB repeatedly
- **Solution**: Cache null/empty values with short TTL (e.g., 60s); use **Bloom filter** to reject obviously invalid keys
- **Staff insight**: At scale, cache penetration can DDoS your database. Always cache negatives.

### Cache Breakdown (Hot Key Expiry)
- **Problem**: Popular key expires; thousands of requests hit DB simultaneously
- **Solution**: **Mutex/semaphore** — only one thread refreshes the key; others wait or serve stale data
- **Staff insight**: Use **stale-while-revalidate** pattern: serve stale cached data while async refresh occurs. Accept brief staleness for availability.

### Cache Avalanche
- **Problem**: Many keys expire at once, overwhelming the backend
- **Solution**: Randomized TTLs, staggered expiry, background refresh
- **Staff insight**: Monitor **cache hit rate** as a leading indicator. Sudden drop indicates avalanche in progress.

### Thundering Herd
- **Problem**: Many threads wake up simultaneously to refresh the same key
- **Solution**: Distributed lock (Redis SETNX), single-flight pattern, request coalescing
- **Staff insight**: Implement **single-flight** at the application level — deduplicate concurrent requests for the same key.

## Cache Consistency Models

| Model | Description | Trade-off |
|-------|-------------|-----------|
| **Strong** | Cache always reflects latest DB state | High write latency, complex |
| **Eventual** | Cache converges to DB state within TTL | Simple, possible stale reads |
| **Session** | User sees their own writes immediately | Read-your-writes guarantee |
| **Stale-While-Revalidate** | Serve stale data, refresh in background | Best availability, brief staleness |

- **Staff insight**: Most systems use **eventual consistency** with TTL. For user-facing data, use **session consistency** — route post-write reads to primary or invalidate user-specific cache on write.

## Common Tools

| Tool | Type | Strengths | Use Case |
|------|------|-----------|----------|
| **Redis** | In-memory DS store | Rich data structures, persistence, pub/sub, Lua | Sessions, leaderboards, rate limiting, caching |
| **Memcached** | Simple in-memory cache | Multi-threaded, simple, distributed | Simple key-value caching, high throughput |
| **Caffeine** | Java in-memory | LRU/LFU, windowed TTL, excellent performance | Application-level caching (Guava successor) |
| **Varnish** | HTTP accelerator | VCL configuration, HTTP-aware | Dynamic web content caching |
| **CDN** | Edge caching | Global distribution, DDoS protection | Static assets, API responses at edge |

## Staff-Level Caching Checklist

1. **Define cache strategy per data type**: Hot data → Redis; static → CDN; computed → application cache
2. **Always set TTL**: Even with event invalidation, TTL prevents stale data accumulation
3. **Add TTL jitter**: Prevent cache stampede with ±10% randomization
4. **Cache null values**: Prevent cache penetration for non-existent keys
5. **Implement stampede protection**: Mutex or single-flight for hot key refresh
6. **Monitor hit rates**: <80% hit rate indicates design problem or wrong TTL
7. **Plan for cache failure**: System should degrade gracefully when cache is unavailable
8. **Size appropriately**: Over-provisioned cache wastes money; under-provisioned causes evictions
