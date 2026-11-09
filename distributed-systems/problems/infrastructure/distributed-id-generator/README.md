# Distributed ID Generator

## Problem Statement

Design a distributed ID generator that produces unique, ordered, and compact identifiers across multiple service instances without a central coordinator. The generated IDs should be suitable as primary keys in databases, support time-based sorting, and avoid the scalability bottlenecks of auto-increment database sequences.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Uniqueness**: Globally unique IDs across all instances and time.
- **Ordering**: IDs are roughly ordered by generation time for database indexing.
- **Compactness**: IDs fit in a 64-bit integer for efficient storage and indexing.
- **High throughput**: Generate 100K+ IDs per second per instance.
- **No central coordinator**: Each instance generates IDs independently.
- **Configurable**: Support multiple ID namespaces (users, orders, products).

### Non-Functional Requirements
- **Low latency**: ID generation in < 100 microseconds.
- **No single point of failure**: System works when individual instances fail.
- **Clock tolerance**: Handle clock skew and NTP adjustments gracefully.
- **Backwards compatible**: Old ID format continues to work during migration.

## Key Design Decisions
- **Snowflake algorithm**: 64-bit ID with timestamp + machine ID + sequence number.
- **Machine ID assignment**: Auto-assign via ZooKeeper/Etcd or manual configuration.
- **Sequence number**: Per-millisecond counter for high-throughput on single machine.
- **Time handling**: Use monotonic clock to prevent duplicate IDs on clock adjustments.

## ID Format (Snowflake)

```
41 bits        10 bits     12 bits
Timestamp      Machine ID  Sequence
(ms precision) (node)      (per ms)

Max IDs: 4096 machines × 4096 seq/ms = 16.7M IDs/ms
Timestamp: ~69 years of ms precision from epoch
```

## Staff-Level Design Considerations

### Snowflake vs Alternatives
- **Snowflake**: Time-ordered, compact, no coordination — best for most use cases.
- **UUID v4**: Random, no ordering — bad for database indexing (page splits).
- **UUID v7**: Time-ordered UUID — good for distributed systems using UUIDs.
- **Database sequence**: Central bottleneck — doesn't scale horizontally.
- **Staff insight**: Use **Snowflake** for primary keys in sharded databases. Use **UUID v7** when you need standard UUID compatibility (e.g., PostgreSQL `uuid` type). Never use random UUIDs (v4) as primary keys in high-write tables — they cause index fragmentation.

### Machine ID Assignment
- **Manual config**: Assign machine IDs during deployment — simple but inflexible.
- **Auto-assign**: Use ZooKeeper ephemeral nodes or Etcd leases for dynamic assignment.
- **Staff insight**: Use **auto-assign with fallback**. On startup, try to claim a machine ID from Etcd. If Etcd is down, use a random ID from a reserved range. Log a warning but don't fail — ID generation must always work.

### Clock Handling
- **Monotonic clock**: Use system monotonic clock for sequence, wall clock for timestamp.
- **Clock drift**: If clock goes backward, reject IDs until clock catches up.
- **Staff insight**: Snowflake **cannot handle clock rollback**. If NTP adjusts clock backward, the generator may produce duplicate IDs. Use `ntpd` with `tinker panic 0` to prevent large clock adjustments, or use a hybrid approach: Snowflake for new IDs, database sequence as fallback.

### Throughput Optimization
- **Batch pre-allocation**: Allocate a batch of IDs (e.g., 1000) from a central service; generate locally until batch is exhausted.
- **Segment approach**: Each instance gets a segment (start, end, step); generates IDs locally.
- **Staff insight**: Use **batch pre-allocation** for maximum throughput. Instead of calling a central service for every ID, allocate 1000 IDs at a time. This reduces central service calls by 1000x. TikTok's Leaf algorithm uses this approach.

### Migration Strategy
- **Dual-write**: Generate both old-style DB auto-increment and Snowflake IDs during migration.
- **Staff insight**: Migrate by **adding a Snowflake column** alongside the existing auto-increment PK. Write both during transition period. Once all services use Snowflake ID, drop the old column. This avoids downtime and allows gradual migration.
