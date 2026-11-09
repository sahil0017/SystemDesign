# Redis

## Overview

Redis is an in-memory data structure store used as a database, cache, and message broker. For staff engineers, Redis is the go-to solution for **low-latency caching**, **distributed rate limiting**, **real-time counters**, **session management**, and **distributed locking**.

## Data Structures

| Structure | Use Case | Staff Insight |
|-----------|----------|---------------|
| **String** | Simple key-value, counters, rate limiting | Use INCR/DECR for atomic counters |
| **Hash** | Objects with fields (user profiles, cart items) | O(1) field access; avoid serializing entire objects |
| **List** | Queues, recent activity feeds | LPUSH/RPOP for simple queues; use Streams for production |
| **Set** | Unique members, tags, followers | SINTER/SUNION for set operations; use for deduplication |
| **Sorted Set** | Leaderboards, ranked lists, scheduled tasks | Score-based ordering; ZRANGEBYSCORE for range queries |
| **Bitmap** | Presence tracking, feature flags | Bit-level operations; 1M users = 125KB |
| **HyperLogLog** | Unique visitor counting | Probabilistic; 0.81% error; 12KB for billions of counts |
| **Stream** | Message queues, event sourcing | Consumer groups; pending messages; ack/nack |
| **Geo** | Geospatial queries | GEORADIUS for nearby locations; stores lat/lon |

## Features

- **Persistence**: RDB (snapshots), AOF (append-only log), or both
- **Replication**: Master-replica for read scaling and high availability
- **Clustering**: Horizontal scaling with automatic sharding (16384 hash slots)
- **Pub/Sub**: Real-time notifications, chat, live updates
- **Lua scripting**: Atomic multi-step operations; reduce round-trips
- **Transactions**: MULTI/EXEC for atomic command groups

## Use Cases

- **Caching**: Multi-tier caching (L1: app, L2: Redis, L3: DB)
- **Session store**: Distributed session management for stateless services
- **Rate limiting**: Token bucket/sliding window with atomic operations
- **Real-time analytics**: Counters, leaderboards, unique visitors
- **Pub/Sub**: Real-time notifications, chat, live updates
- **Distributed lock**: Redlock algorithm for distributed coordination
- **Job queue**: Background job processing with Streams

## Key Design Decisions

### Persistence
- **RDB**: Point-in-time snapshots; faster; possible data loss
- **AOF**: Append-only log; durable; slower; larger files
- **Both**: RDB + AOF for best of both worlds (Redis 4.0+)
- **Staff insight**: Use **RDB + AOF** for production. RDB for fast restart; AOF for durability.

### High Availability
- **Redis Sentinel**: Automatic failover; quorum-based leader election
- **Redis Cluster**: Horizontal scaling; automatic sharding; 16384 hash slots
- **Staff insight**: Use **Sentinel** for HA without sharding; **Cluster** for sharding + HA.

## Staff-Level Redis Checklist

1. **Use connection pooling**: Avoid per-request connection overhead
2. **Set TTL on all keys**: Prevent memory leaks; use randomized TTL for jitter
3. **Use pipelining**: Batch commands for reduced round-trips
4. **Monitor memory usage**: Maxmemory policy (allkeys-lru) for cache eviction
5. **Use Lua scripts**: Atomic multi-step operations; reduce round-trips
6. **Avoid blocking commands**: BLPOP, BRPOP can block; use with timeout
7. **Use Redis Streams for production queues**: More reliable than Lists
8. **Plan for failover**: Sentinel for automatic failover; client-side retry logic
- Leaderboards
- Real-time analytics
- Message queue
