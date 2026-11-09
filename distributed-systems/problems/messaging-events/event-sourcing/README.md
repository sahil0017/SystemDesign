# Event Sourcing

## Problem Statement

Design an event sourcing system where application state is stored as an immutable sequence of events rather than just the current state. This pattern enables audit trails, temporal queries, event replay, and reliable event-driven architecture for complex business domains.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Event store**: Append-only storage for domain events with guaranteed ordering per aggregate.
- **Aggregate reconstruction**: Rebuild current state by replaying events from the event store.
- **Event versioning**: Handle schema evolution without breaking old event replay.
- **Snapshots**: Periodic state snapshots to avoid replaying all events for large aggregates.
- **Projections**: Build read models (CQRS views) from event streams.
- **Compensation**: Support compensating events for undoing business operations.

### Non-Functional Requirements
- **Durability**: Events are never lost or modified once stored.
- **Ordering**: Events for the same aggregate are strictly ordered.
- **Performance**: Read current state in < 10ms without full replay.
- **Scalability**: Handle 100K events/second across multiple aggregates.

## Key Design Decisions
- **Append-only store**: Events are never updated or deleted; corrections are new events.
- **Optimistic concurrency**: Version check on aggregates prevents lost updates.
- **Snapshot strategy**: Take snapshot every N events to speed up aggregate loading.
- **Event schema evolution**: Use Avro/Protobuf with backward-compatible schema changes.

## Architecture

```
Write Side                    Event Store                  Read Side
Command --> Aggregate --> Event --> Kafka --> EventDB
                                    |
                                    v
                              Projection Service
                                    |
                                    v
                              Read Model DB (Query API)
```

## Staff-Level Design Considerations

### Event Immutability
- **Never modify events**: Once stored, events are immutable facts about what happened.
- **Corrections are new events**: If an order was created with wrong price, emit `OrderPriceCorrected` event.
- **Staff insight**: Event immutability is the foundation of auditability. Never allow `UPDATE` or `DELETE` on the event store. Regulatory compliance (SOX, HIPAA) requires this.

### Aggregate Design
- **Bounded context**: Each aggregate represents a single consistency boundary.
- **Version checking**: On save, check `expectedVersion == currentVersion` to prevent lost updates.
- **Staff insight**: Keep aggregates **small** — a large aggregate with many events becomes slow to load. If an aggregate grows beyond 10K events, consider splitting it into smaller aggregates.

### Snapshot Strategy
- **When to snapshot**: After N events (e.g., every 100 events) or on time-based schedule.
- **Snapshot storage**: Store alongside events with version marker.
- **Staff insight**: Snapshots trade storage for speed. For aggregates with few events (most orders), skip snapshots. For aggregates with many events (user profiles, accounts), snapshot every 100-500 events.

### Event Schema Evolution
- **Backward compatibility**: New readers can read old events; old readers can read new events.
- **Additive changes only**: Add new fields with defaults; never remove or rename fields.
- **Staff insight**: Use **Avro with schema registry** — Avro stores field IDs, not names, so adding/removing fields doesn't break serialization. Schema registry enforces compatibility rules on publish.

### Projection Management
- **Multiple projections**: Same event stream can build different read models for different queries.
- **Rebuild capability**: Projections can be rebuilt from scratch by replaying all events.
- **Staff insight**: Design projections as **independent services** that consume from the event stream. If a projection's query needs change, rebuild it without affecting the write side. This is the power of CQRS + Event Sourcing.
