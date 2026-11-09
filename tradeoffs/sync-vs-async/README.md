# Sync vs Async Communication

## Trade-off Overview

Synchronous (REST/gRPC) and asynchronous (message queues) communication each have distinct trade-offs in latency, reliability, and system coupling.

## Synchronous (REST/gRPC)

### Pros
- **Simple**: Request-response pattern is intuitive to implement and debug.
- **Low latency**: Direct response without queue overhead.
- **Strong consistency**: Caller waits for result; data is consistent on return.
- **Error handling**: Immediate feedback on success/failure.

### Cons
- **Tight coupling**: Caller depends on callee's availability and performance.
- **Cascading failures**: Downstream failure propagates to caller.
- **Scaling**: Caller and callee must scale together.

## Asynchronous (Message Queues)

### Pros
- **Loose coupling**: Producer doesn't depend on consumer's availability.
- **Buffering**: Queue absorbs traffic spikes; consumers process at their pace.
- **Fan-out**: One message can trigger multiple consumers.
- **Resilience**: Failed consumers retry; messages are not lost.

### Cons
- **Complexity**: Eventual consistency, idempotency, ordering challenges.
- **Latency**: Message processing adds delay (milliseconds to minutes).
- **Debugging**: Hard to trace async flows across services.

## Decision Framework

| Factor | Choose Sync When... | Choose Async When... |
|--------|-------------------|---------------------|
| Response needed | Immediate response required | Response can be delayed |
| Coupling | Tight coupling acceptable | Loose coupling preferred |
| Throughput | Low to moderate | High throughput, bursty traffic |
| Consistency | Strong consistency needed | Eventual consistency acceptable |

## Staff-Level Insight

> "Use sync for request-response, async for event-driven. Most systems need both."

- **Sync for reads**: User requests data → sync REST/gRPC call → return result.
- **Async for writes**: User creates order → async event → inventory, payment, shipping process independently.
- **Staff insight**: Use **async for cross-service writes** to prevent cascading failures. If payment service is slow, the order service shouldn't block. Use **sync for reads** where users expect immediate responses. Combine with **circuit breaker** for sync calls and **dead letter queue** for async messages.
