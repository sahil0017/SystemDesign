# API Rate Limiter

## Problem Statement

Design a distributed API rate limiter that controls the number of requests a client can make within a time window, supporting multiple algorithms, per-user and global limits, and real-time enforcement.

**Reference**: ByteByteGo, Educative.io, HelloInterview

## Requirements

### Functional Requirements
- **Rate limiting algorithms**: Token bucket, sliding window log, fixed window counter.
- **Per-user limits**: Different limits per API key, user tier, or endpoint.
- **Global limits**: System-wide rate limits to protect backend services.
- **Quota management**: Daily/monthly quotas in addition to per-second limits.
- **Headers**: Return remaining quota, reset time, and limit in response headers.
- **Burst support**: Allow short bursts above the average rate.

### Non-Functional Requirements
- **Scale**: 100M+ API keys; 10M+ requests per second.
- **Latency**: Rate limit check < 1ms (must not add significant overhead).
- **Consistency**: Distributed rate limiting with eventual consistency.

## Key Design Decisions
- **Token bucket**: Best for burst support; tokens refill at a constant rate.
- **Sliding window log**: Most accurate; stores timestamps of each request.
- **Redis backend**: Atomic operations (INCR, EXPIRE) for distributed counting.
- **Local + distributed**: Two-tier rate limiting — local cache for fast path, Redis for accuracy.

## Architecture Overview

```
Client → Load Balancer → API Gateway
                                → Rate Limiter (local cache)
                                → Rate Limiter (Redis cluster)
                                → Backend Services
```

## Staff-Level Design Considerations

### Algorithm Selection
- **Token bucket**: Best for APIs that need burst support. Tokens refill at rate R; bucket size B allows bursts up to B.
- **Sliding window log**: Most accurate but memory-intensive. Store each request timestamp in a sorted set.
- **Staff insight**: Use token bucket for most APIs. Use sliding window for APIs where accuracy matters more than memory (e.g., financial APIs).

### Distributed Rate Limiting
- **Redis INCR + EXPIRE**: Atomic increment with TTL. Simple but has boundary problems at window edges.
- **Staff insight**: For distributed rate limiting, use Redis with a sliding window log (sorted set). Each request adds a timestamped entry. Count entries in the window with ZRANGEBYSCORE. This is O(log n) and accurate.

### Two-Tier Design
- **Local cache**: In-memory token bucket per API gateway instance. Allows requests even when Redis is down.
- **Staff insight**: This is a circuit breaker pattern. If Redis is unavailable, fall back to local rate limiting. It's less accurate but keeps the system available. Reconcile with Redis when it's back.
