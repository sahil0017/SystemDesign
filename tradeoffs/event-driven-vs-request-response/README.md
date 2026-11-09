# Event-Driven vs Request-Response

## Trade-off Overview

Event-driven architecture reacts to events asynchronously. Request-response architecture processes synchronous requests with immediate responses.

## Event-Driven (Kafka, Event Bus)
- **Pros**: Loose coupling, scalability, resilience, event sourcing, audit trail.
- **Cons**: Eventual consistency, complex debugging, ordering challenges.
- **Use when**: Async workflows, fan-out, audit requirements, decoupled services.

## Request-Response (REST, RPC)
- **Pros**: Simple, immediate feedback, strong consistency, easy debugging.
- **Cons**: Tight coupling, cascading failures, scaling limitations.
- **Use when**: User-facing APIs, immediate results needed, simple workflows.

## Staff-Level Insight

> "Event-driven for backend workflows, request-response for user-facing APIs."

- **Staff insight**: Use **event-driven for cross-service workflows** (order placed → inventory, payment, shipping). Use **request-response for user-facing APIs** (get order status, update profile). Combine both: user makes sync request → service publishes event → async processing → user polls or receives WebSocket notification for result. This is the **command-query separation** pattern in practice.
