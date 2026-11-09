# Resilience & Fault Tolerance

Patterns and systems that protect distributed services from cascading failures, handle downstream dependency outages, and enforce request quotas across multiple instances.

## Problems (2)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Circuit Breaker](circuit-breaker/) | Protect microservices from cascading failures on dependency outage | Three states, failure detection, fallback, distributed state |
| [Distributed Rate Limiter](distributed-rate-limiter/) | Enforce request quotas across multiple service instances | Token bucket, sliding window, Redis Lua, local cache |

## When to Use

- **Circuit Breaker**: When any service calls downstream dependencies that may fail (e.g., payment gateway, external API, database). Prevents cascading failures and enables graceful degradation.
- **Distributed Rate Limiter**: When you must enforce per-user or per-API quotas across horizontally scaled instances (e.g., API rate limits, abuse prevention, fair usage policies).

## Cross-References

- **Topics**: [Idempotency](../../idempotency/), [Redis](../../redis/)
- **Related**: [Distributed Cache](../data-management/distributed-cache/) provides the backing store for rate limiter counters. Circuit breakers complement the [Saga Pattern](../../saga-pattern/) by handling partial failures.
