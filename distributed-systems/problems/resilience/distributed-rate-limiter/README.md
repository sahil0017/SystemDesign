# Distributed Rate Limiter

## Problem Statement

Design a distributed rate limiter that enforces request quotas across multiple service instances. The system must support various rate limiting algorithms, per-user/per-API quotas, sliding windows, and real-time counter synchronization without becoming a bottleneck.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Algorithms**: Token bucket, sliding window log, fixed window counter, leaky bucket.
- **Granularity**: Rate limit by user, IP, API key, endpoint, or combinations.
- **Quota management**: Configurable limits (requests/second, requests/minute, daily quotas).
- **Counter synchronization**: Shared counters across service instances via distributed store.
- **Burst handling**: Allow controlled bursts above the rate limit with token bucket refill.
- **Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` in responses.

### Non-Functional Requirements
- **Low latency**: Rate limit check adds < 1ms to request processing.
- **Accuracy**: Counters are accurate within ±5% across distributed instances.
- **Scalability**: Handle 1M+ rate limit checks per second.
- **Fault tolerance**: If rate limiter is down, allow requests (fail-open) or reject (fail-closed).

## Key Design Decisions
- **Redis-backed**: Use Redis for atomic counter operations with Lua scripts.
- **Sliding window log**: Most accurate algorithm; stores timestamps of each request.
- **Local cache**: Cache counters locally with short TTL to reduce Redis calls.
- **Fail-open**: If Redis is down, allow requests to prevent service outage.

## Architecture

```
Client --> API Gateway --> Rate Limiter Middleware --> Service
                              |
                              +-- Local Cache (1s TTL)
                              |
                              +-- Redis Cluster (Atomic Lua Script)
                                   |
                                   +-- INCRBY + EXPIRE (Fixed Window)
                                   +-- ZADD + ZRANGEBYSCORE (Sliding Window)
```

## Staff-Level Design Considerations

### Algorithm Selection
- **Fixed window**: Simple but allows 2x burst at window boundaries.
- **Sliding window log**: Most accurate; stores each request timestamp; memory-intensive.
- **Token bucket**: Allows controlled bursts; best for API rate limiting.
- **Staff insight**: Use **token bucket** for API rate limiting — it allows natural burst patterns (e.g., page load makes multiple requests at once) while enforcing average rate. Use **sliding window** for strict compliance (e.g., regulatory limits).

### Redis Implementation
- **Lua script**: Atomic check-and-increment in a single Redis call.
- **Key design**: `rate:{user_id}:{endpoint}:{window}` with TTL = window size.
- **Staff insight**: Use **Redis Lua scripts** for atomicity. A non-atomic check-then-increment has a race condition: two requests can both see count < limit and both increment, exceeding the limit.

### Local Caching
- **Cache counters**: Store local count with 1-second TTL; batch sync to Redis.
- **Over-count risk**: Local cache may allow slightly more requests than limit.
- **Staff insight**: Accept **±5% accuracy** for rate limiting. Perfect accuracy requires every request to hit Redis, which doesn't scale. Local cache with short TTL reduces Redis load by 90% while maintaining acceptable accuracy.

### Distributed Counter Sync
- **Redis Cluster**: Slot-based partitioning distributes rate limit keys across nodes.
- **Staff insight**: Hash rate limit keys by user ID so all a user's limits land on the same Redis node. This enables **atomic multi-key operations** (e.g., check both per-user and per-endpoint limits atomically).

### Fail-Open vs Fail-Closed
- **Fail-open**: If rate limiter is down, allow all requests — protects availability.
- **Fail-closed**: If rate limiter is down, reject all requests — protects backend.
- **Staff insight**: Use **fail-open for external APIs** (don't block legitimate users) and **fail-closed for internal services** (protect downstream from overload). Make this configurable per endpoint.
