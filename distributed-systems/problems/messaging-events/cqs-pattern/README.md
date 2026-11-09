# CQRS Pattern (Command Query Responsibility Segregation)

## Problem Statement

Design a system using the CQRS pattern where command (write) and query (read) operations use separate models. This pattern enables independent scaling of reads and writes, optimized data models for each access pattern, and better handling of complex write logic without compromising read performance.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Command model**: Handle write operations with business logic validation, domain rules, and persistence.
- **Query model**: Handle read operations with optimized data structures for specific query patterns.
- **Event synchronization**: Commands emit events that update query models asynchronously.
- **Multiple read models**: Support different query projections (e.g., list view, detail view, search view).
- **Consistency handling**: Manage eventual consistency between command and query models.

### Non-Functional Requirements
- **Read performance**: Query responses in < 10ms via optimized read models.
- **Write consistency**: Commands are strongly consistent within the write model.
- **Eventual consistency**: Read models catch up within < 1 second of command completion.
- **Scalability**: Scale read and write models independently based on load.

## Key Design Decisions
- **Separate models**: Command model enforces domain rules; query model optimizes for access patterns.
- **Event-driven sync**: Commands publish events; query models subscribe and update projections.
- **Read model denormalization**: Query models denormalize data for fast reads without joins.
- **Consistency communication**: Return command acceptance immediately; poll or use WebSocket for read model updates.

## Architecture

```
Client
  |
  +-- Command --> Command Handler --> Domain Model --> Event Store --> Kafka
  |                                                              |
  |                                                              v
  |                                                      Projection Service
  |                                                              |
  |                                                              v
  +-- Query <---- Query Handler <---- Read Model DB (Denormalized)
```

## Staff-Level Design Considerations

### When to Use CQRS
- **High read/write ratio**: Social feeds, dashboards, monitoring systems benefit most.
- **Complex write logic**: Financial systems, booking systems with many business rules.
- **Multiple read formats**: Same data needed in list, detail, search, and analytics views.
- **Staff insight**: **Don't use CQRS for CRUD apps**. If your read model is the same as your write model, CQRS adds complexity without benefit. Start with a unified model; split when you hit scaling or complexity limits.

### Consistency Management
- **Eventual consistency**: Read models lag behind writes by milliseconds to seconds.
- **Optimistic UI**: Show expected state immediately; correct when read model catches up.
- **Staff insight**: Design the **user experience** around eventual consistency. Show "Your order is being processed" immediately, then update to "Confirmed" when the read model reflects the change. Use WebSockets for real-time updates where needed.

### Read Model Design
- **Query-driven**: Design read models based on actual query patterns, not domain concepts.
- **Denormalization**: Embed related data to avoid joins — store order items with order, user name with posts.
- **Staff insight**: Each read endpoint should have its own **optimized table or index**. Don't try to build one universal read model. A list view needs different data than a detail view — optimize each independently.

### Command Validation
- **Write-side validation**: Check business rules against the command model (source of truth).
- **Read-side feedback**: Use read models for UI validation (e.g., "username taken") but always revalidate on write.
- **Staff insight**: Never trust read model data for business rule validation. It's eventually consistent. Always validate against the command model, which is the source of truth.

### Performance Trade-offs
- **Write latency**: Commands must persist events before acknowledging — adds latency.
- **Read latency**: Read models are denormalized and cached — very fast reads.
- **Staff insight**: CQRS shifts latency from reads to writes. If your system is write-heavy (e.g., IoT sensor ingestion), CQRS may not help. It shines when reads >> writes (e.g., e-commerce catalog, social feeds).
