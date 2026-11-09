# Distributed Unique ID Generator

## Problem Statement

Design a distributed unique ID generator like Twitter's Snowflake that generates globally unique, sortable IDs at high throughput across multiple nodes.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Uniqueness**: Globally unique IDs across all nodes and time.
- **Sortability**: IDs are sortable by creation time (timestamp in MSB).
- **High throughput**: 100K+ IDs per second per node.
- **Compact**: 64-bit IDs that fit in standard integer columns.
- **Trendability**: IDs should be mostly increasing for database insert optimization.

### Non-Functional Requirements
- **Scale**: 100+ generating nodes; 10M+ IDs per second total.
- **Latency**: ID generation < 1ms (in-memory, no network call).
- **Fault tolerance**: Continue generating IDs if individual nodes fail.

## Key Design Decisions
- **Snowflake format**: 1 bit sign + 41 bits timestamp + 10 bits node ID + 12 bits sequence.
- **Timestamp handling**: Handle clock rollback with configurable strategy (wait or fail).
- **Sequence number**: Per-second sequence counter for multiple IDs per millisecond.
- **Node ID**: Pre-assigned or auto-discovered via service registry.

## Architecture Overview

```
ID Generator Node (in-memory, no network)
├── Timestamp (41 bits) = milliseconds since custom epoch
├── Node ID (10 bits) = unique node identifier (0-1023)
└── Sequence (12 bits) = sequence number within millisecond (0-4095)

Format: [Sign][Timestamp: 41 bits][Node ID: 10 bits][Sequence: 12 bits]
        0      0000000 000000000000000000  000000  000000000000
```

## Staff-Level Design Considerations

### Snowflake Limitations
- **41-bit timestamp**: ~69 years from epoch. Set epoch to 2020-01-01 for ~49 years of use.
- **12-bit sequence**: 4,096 IDs per millisecond per node. With 1,024 nodes: 4M IDs/ms total.
- **Staff insight**: If you exceed 4,096 IDs/ms on a single node, you need to wait for the next millisecond. This is a backpressure mechanism. If your system needs more, increase sequence bits or use a different algorithm.

### Clock Rollback Handling
- **Problem**: NTP sync can cause clock to go backward, generating duplicate IDs.
- **Staff insight**: Three strategies: (1) Wait until clock catches up (simple, adds latency). (2) Fail and retry (safe, hurts throughput). (3) Use logical clocks (Hybrid Logical Clock) that combine physical and logical time. Option 3 is what Google uses in TrueTime.

### Alternatives
- **UUID v4**: Random, unique, but not sortable. Bad for database indexes.
- **UUID v7**: New standard with timestamp prefix. Sortable but 128 bits (larger storage).
- **Staff insight**: Snowflake is best for sortable, compact IDs. UUID v7 is a good alternative if you don't need the Snowflake structure. Database sequences (PostgreSQL) work for single-node but not distributed.
