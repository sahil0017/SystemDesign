# Circuit Breaker Pattern

## Problem Statement

Design and implement a distributed circuit breaker pattern that protects microservices from cascading failures when downstream dependencies become unavailable. The circuit breaker should automatically detect failures, open the circuit to prevent further calls, and gradually restore service through half-open probing.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Three states**: Closed (normal), Open (failing), Half-Open (probing).
- **Failure detection**: Track failure rate, consecutive failures, or latency thresholds.
- **Automatic state transitions**: Closed → Open on threshold breach; Open → Half-Open after timeout; Half-Open → Closed on success or → Open on failure.
- **Fallback handling**: Execute fallback logic when circuit is open.
- **Metrics**: Track failure count, success count, latency percentiles, state changes.
- **Per-service configuration**: Different thresholds and timeouts per downstream dependency.

### Non-Functional Requirements
- **Low overhead**: Circuit breaker check should add < 1ms latency.
- **Thread-safe**: Handle concurrent requests without race conditions.
- **Distributed state**: Share circuit state across service instances for consistent behavior.
- **Configurable**: Update thresholds without restart via config service.

## Key Design Decisions
- **Sliding window**: Use sliding time window for failure rate calculation instead of fixed window.
- **Distributed state**: Store circuit state in Redis with TTL for shared state across instances.
- **Fallback strategies**: Return cached data, default value, or graceful degradation.
- **Health check integration**: Circuit breaker state exposed via health endpoint.

## Architecture

```
Client Service          Circuit Breaker          Downstream Service
     |                       |                          |
     |--- request --------->|                          |
     |                       |--- request ----------->|
     |                       |<-- response ----------|
     |<-- response ---------|                          |
     |                       |                          |
     | (if failures > threshold)                        |
     |                       | [Circuit OPEN]           |
     |--- request --------->|                          |
     |<-- fallback ---------|                          |
```

## Staff-Level Design Considerations

### Failure Rate vs Consecutive Failers
- **Failure rate**: More accurate; handles intermittent failures better. Use sliding window of last N requests.
- **Consecutive failures**: Simpler; triggers faster on sustained failures but misses intermittent issues.
- **Staff insight**: Use **failure rate with sliding window** (e.g., >50% failures in last 100 requests) for production systems. Consecutive failures are too aggressive for systems with occasional blips.

### Distributed Circuit State
- **Local-only**: Each instance maintains its own state — fast but inconsistent.
- **Shared state**: Redis stores global failure count — consistent but adds latency.
- **Staff insight**: Use **hybrid approach** — local circuit breaker for speed, but broadcast state changes via Redis pub/sub so instances converge quickly. This gives both low latency and eventual consistency.

### Half-Open Probing
- **Single probe**: Allow one request through; if it succeeds, close circuit.
- **Gradual restore**: Allow increasing percentage of requests (10% → 25% → 50% → 100%).
- **Staff insight**: Use **gradual restore** to avoid thundering herd when circuit closes. A single probe can succeed by luck, then the downstream service gets flooded again.

### Fallback Strategies
- **Cached data**: Return stale cached response — acceptable for read operations.
- **Default value**: Return empty list or default — acceptable for non-critical features.
- **Graceful degradation**: Disable feature entirely — show "feature unavailable" message.
- **Staff insight**: Design fallbacks as **first-class citizens**, not afterthoughts. Document what each fallback returns and test them in chaos engineering exercises.

### Monitoring and Alerting
- **State changes**: Alert on circuit open events — indicates downstream dependency issues.
- **Failure rate**: Track failure rate trends — increasing rate before threshold breach predicts upcoming circuit open.
- **Staff insight**: Circuit breaker metrics are **leading indicators** of system health. Alert on failure rate trends, not just circuit state changes.
