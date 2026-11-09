# Event Sourcing & CQRS

## Overview

Event Sourcing stores application state as an immutable sequence of events, while CQRS (Command Query Responsibility Segregation) separates read and write models. Together, they enable auditability, temporal queries, and independent scaling of reads and writes.

## Event Sourcing

### Core Concept
Instead of storing just the current state, store every change as an event:
```
Traditional:  User { name: "John", email: "john@example.com" }
Event Sourcing:
  - UserCreated { name: "John", email: "john@old.com" }
  - UserEmailChanged { newEmail: "john@example.com" }
```

### Reconstructing State
- Current state = apply all events in order
- **Snapshots**: Periodically save state to avoid replaying all events
- **Event versioning**: Handle schema evolution with backward-compatible changes

### Benefits
- **Audit trail**: Every change is recorded with timestamp and reason
- **Temporal queries**: Query state at any point in time
- **Event replay**: Rebuild state or projections from scratch
- **Debugging**: Replay events to reproduce bugs

## CQRS Pattern

### Separation of Concerns
```
Write Side (Commands)          Read Side (Queries)
     |                              |
Command → Handler → Domain    Query → Handler → Read Model
     |                              |
     └──→ Events → Kafka ──→ Projection → Read Model DB
```

### Write Model
- Enforces business rules and domain invariants
- Persists events (not state)
- Strongly consistent within the aggregate

### Read Model
- Denormalized data optimized for query patterns
- Built from events via projections
- Eventually consistent with write model

### Multiple Read Models
- Same events can build different views:
  - List view: Summary data for listing
  - Detail view: Full data for detail page
  - Search view: Indexed data for search

## When to Use

### Good Fit
- **Complex domain logic**: Financial systems, booking systems
- **High read/write ratio**: Social feeds, dashboards
- **Audit requirements**: Regulatory compliance, financial records
- **Multiple read formats**: Same data needed in different views

### Bad Fit
- **Simple CRUD apps**: Overhead without benefit
- **Real-time consistency needed**: Eventual consistency is a trade-off
- **Write-heavy systems**: Event storage and processing overhead

## Staff-Level Insights

### Aggregate Design
- Keep aggregates **small** — large aggregates with many events are slow to load
- Each aggregate is a **consistency boundary** — don't span multiple aggregates
- **Staff insight**: If an aggregate grows beyond 10K events, consider splitting it. Use snapshots every 100-500 events to speed up loading.

### Consistency Management
- Read models are **eventually consistent** — lag behind writes by milliseconds to seconds
- Design UX around this: show "processing" state, then update when read model catches up
- **Staff insight**: Use **optimistic UI** — show expected state immediately, correct when read model updates. For critical operations, use WebSockets for real-time updates.

### Event Schema Evolution
- Use **Avro with schema registry** for backward-compatible schema changes
- Additive changes only: add fields with defaults, never remove or rename
- **Staff insight**: Event schema evolution is the #1 challenge in event sourcing. Plan for it from day one. Use schema registry to enforce compatibility rules on publish.

### Projection Management
- Projections are **independent services** consuming from the event stream
- If a query needs change, rebuild the projection without affecting the write side
- **Staff insight**: Design projections to be **rebuildable from scratch**. This is the power of event sourcing — you can always rebuild read models by replaying events.
