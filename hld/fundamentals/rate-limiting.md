# Rate Limiting

## Overview

Rate limiting controls the number of requests a client can make in a given time period to prevent **abuse**, **overload**, and **ensure fair usage**. For staff engineers, rate limiting is a critical **defense-in-depth** mechanism that protects systems from DDoS, API abuse, and cascade failures.

## Algorithms

### Fixed Window
- **How it works**: Count requests in fixed time windows (e.g., 100 requests per minute); reset at window boundary
- **Pros**: Simple to implement; low memory usage; easy to understand
- **Cons**: **Burst at boundaries** — client can send 200 requests in 2 minutes (100 at end of one window + 100 at start of next)
- **Implementation**: Redis INCR + EXPIRE; hash map with timestamps
- **Staff insight**: Fixed window is acceptable for **coarse-grained** limits (e.g., daily quotas). Avoid for per-second limits where burst matters.

### Sliding Window Log
- **How it works**: Track timestamp of each request; count requests within rolling window
- **Pros**: **Precise rate limiting**; no burst at boundaries; accurate enforcement
- **Cons**: **High memory usage** — stores every request timestamp; O(n) cleanup
- **Implementation**: Sorted set in Redis (ZADD with timestamp); periodic cleanup of old entries
- **Staff insight**: Use for **high-value** rate limits (e.g., payment APIs, login attempts). Memory cost is acceptable for critical endpoints.

### Sliding Window Counter
- **How it works**: Hybrid of fixed and sliding — weight current + previous window counts
- **Formula**: `count = prev_window_count * (1 - progress) + current_window_count`
- **Pros**: **Approximate sliding window** with low memory; smooth enforcement
- **Cons**: Slightly less precise than sliding window log
- **Staff insight**: Best **practical choice** for most systems. Good accuracy with O(1) memory per client.

### Token Bucket
- **How it works**: Bucket starts full; tokens added at fixed rate; each request consumes a token; excess requests rejected
- **Pros**: **Allows controlled bursts** up to bucket size; smooth average rate; intuitive
- **Cons**: Burst size = bucket capacity; needs tuning
- **Implementation**: Redis with Lua script; in-memory with periodic refill
- **Staff insight**: Token bucket is the **default choice** for API rate limiting. It allows legitimate bursts (e.g., page load with multiple API calls) while enforcing average rate.

### Leaky Bucket
- **How it works**: Requests enter a queue; processed at fixed rate; excess requests rejected when queue full
- **Pros**: **Smooths traffic** to backend; constant output rate; predictable load
- **Cons**: **Adds latency** — requests wait in queue; queue management overhead
- **Implementation**: Queue with fixed drain rate; timer-based processing
- **Staff insight**: Leaky bucket is best for **protecting downstream services** with fixed capacity. Use when backend has known throughput limit.

### Algorithm Comparison

| Algorithm | Burst Allowed | Precision | Memory | Complexity | Best For |
|-----------|--------------|-----------|--------|------------|----------|
| **Fixed Window** | High (at boundaries) | Low | O(1) | Simple | Daily quotas, coarse limits |
| **Sliding Window Log** | None | High | O(n) | Complex | Critical APIs, security |
| **Sliding Window Counter** | Low | Medium | O(1) | Medium | General-purpose |
| **Token Bucket** | Configurable | High | O(1) | Medium | API rate limiting |
| **Leaky Bucket** | None (queued) | High | O(queue) | Medium | Backend protection |

## Implementation Levels

| Level | Where | Pros | Cons |
|-------|-------|------|------|
| **CDN/Edge** | Cloudflare, CloudFront | Global; offloads origin; DDoS protection | Limited customization |
| **API Gateway** | Kong, Apigee, AWS API Gateway | Centralized; policy management; observability | Single point of failure |
| **Service Level** | In-application, sidecar | Fine-grained; per-service tuning | Distributed state needed |
| **Database Level** | Query limits, connection limits | Protects most critical resource | Late in request chain |

- **Staff insight**: Use **multi-layer rate limiting**: CDN for DDoS, API gateway for per-client limits, service level for per-endpoint limits. Each layer catches different attack vectors.

## Rate Limiting Strategies

### Per-Client Limiting
- **By API key**: Most common; ties limit to authenticated user
- **By IP address**: For unauthenticated endpoints; vulnerable to IP sharing
- **By user ID**: For authenticated users; most accurate
- **Staff insight**: Use **API key + user ID** for authenticated endpoints. For unauthenticated, use **IP + User-Agent** to reduce false positives.

### Per-Endpoint Limiting
- **How it works**: Different limits for different endpoints (e.g., /login: 5/min, /search: 30/min)
- **Rationale**: Expensive endpoints need stricter limits
- **Staff insight**: Classify endpoints by **cost**: cheap (read cache), medium (DB query), expensive (compute, external API). Set limits inversely proportional to cost.

### Global Limiting
- **How it works**: Total system-wide limit regardless of client
- **Use case**: Protect backend capacity during traffic spikes
- **Staff insight**: Use **adaptive global limits** that adjust based on backend health metrics (CPU, queue depth, error rate).

## Distributed Rate Limiting

### Challenges
- **State synchronization**: Multiple instances need shared counter
- **Latency**: Rate limit check should not add significant latency
- **Consistency**: Over/under-limiting during clock skew or network delay

### Solutions
| Approach | How It Works | Trade-off |
|----------|-------------|-----------|
| **Centralized (Redis)** | All instances check Redis for limits | Redis is bottleneck; single point of failure |
| **Local + Sync** | Each instance tracks locally; periodic sync | Possible over-limiting during sync gap |
| **Token Bucket in Redis** | Lua script for atomic check + decrement | Redis dependency; but atomic and fast |
| **Sliding Window in Redis** | Sorted set with timestamps | Memory intensive for high-cardinality |

- **Staff insight**: **Redis + Lua script** is the standard for distributed rate limiting. Lua ensures atomic check-and-decrement. Use **Redis Cluster** for high availability. For ultra-low latency, use **local cache + Redis sync** with slight over-limiting tolerance.

## Response Handling

| Status Code | Meaning | When to Use |
|-------------|---------|-------------|
| **429 Too Many Requests** | Standard rate limit response | Always include `Retry-After` header |
| **503 Service Unavailable** | System overload | Global rate limit exceeded |
| **403 Forbidden** | Permanent ban | Repeated abuse after warnings |

### Headers to Include
```
X-RateLimit-Limit: 100          # Max requests allowed
X-RateLimit-Remaining: 42       # Requests remaining in window
X-RateLimit-Reset: 1609459200   # Unix timestamp when limit resets
Retry-After: 30                 # Seconds to wait before retrying
```
- **Staff insight**: Always include rate limit headers. Clients can adjust behavior based on remaining quota. Use **Retry-After** to prevent retry storms.

## Use Cases

| Use Case | Algorithm | Limit | Rationale |
|----------|-----------|-------|-----------|
| **API Abuse Prevention** | Token Bucket | Per-client, per-endpoint | Controlled bursts; fair usage |
| **DDoS Protection** | Fixed Window | Per-IP, global | Simple; high throughput |
| **Login Protection** | Sliding Window | Per-IP, per-user | Precise; security-critical |
| **Backend Protection** | Leaky Bucket | Global | Smooth traffic; capacity match |
| **Fair Usage** | Token Bucket | Per-tier (free/pro/enterprise) | Tiered limits; business model |

## Common Tools

| Tool | Type | Features |
|------|------|----------|
| **Redis + Lua** | Custom | Atomic operations; flexible; industry standard |
| **Nginx limit_req** | Reverse proxy | Built-in; token bucket; per-IP |
| **Cloudflare WAF** | CDN | DDoS protection; bot management; managed |
| **Kong Plugin** | API Gateway | Per-client; per-endpoint; Redis-backed |
| **Resilience4j** | Java library | In-memory; sliding window; circuit breaker |
| **Bucket4j** | Java library | Token bucket; distributed; Guava/Redis |

## Staff-Level Rate Limiting Checklist

1. **Use multi-layer limiting**: CDN → API Gateway → Service → Database
2. **Choose token bucket for APIs**: Allows bursts; enforces average rate
3. **Include rate limit headers**: Enable client-side backoff
4. **Use Redis + Lua for distributed limits**: Atomic and performant
5. **Set different limits per endpoint**: Expensive endpoints get stricter limits
6. **Implement graceful degradation**: Return 429 with Retry-After, not 500
7. **Monitor rate limit hits**: High rejection rate indicates limit too strict or attack
8. **Plan for limit bypass**: API key sharing, IP rotation, bot detection
