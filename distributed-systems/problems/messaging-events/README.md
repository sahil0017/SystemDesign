# Messaging & Events

Event-driven architecture patterns for reliable message delivery, state reconstruction from events, and separating read/write concerns in distributed systems.

## Problems (2)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Event Sourcing](event-sourcing/) | Store state as immutable event sequences for audit and replay | Append-only store, snapshots, projections, schema evolution |
| [CQRS Pattern](cqs-pattern/) | Separate command and query models for independent scaling | Command/query separation, read models, eventual consistency |

## When to Use

- **Event Sourcing**: When you need a complete audit trail, temporal queries, or the ability to rebuild state from history (e.g., financial transactions, order management, compliance-heavy domains).
- **CQRS Pattern**: When read and write workloads have different scaling needs or when complex write logic shouldn't compromise read performance (e.g., social feeds, dashboards, e-commerce catalogs).

## Cross-References

- **Topics**: [Kafka](../../kafka/), [Outbox Pattern](../../outbox-pattern/), [Saga Pattern](../../saga-pattern/)
- **Related**: Event Sourcing and CQRS are often used together — events from the write side feed multiple read-side projections.
