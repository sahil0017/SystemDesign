# Consistency vs Availability (CAP Theorem)

## Trade-off Overview

The CAP theorem states that a distributed system can provide at most two of three guarantees: Consistency, Availability, and Partition Tolerance. Since partition tolerance is mandatory in distributed systems, the real choice is between Consistency (CP) and Availability (AP).

## Consistency (CP)

### Characteristics
- Every read receives the most recent write or an error.
- During network partitions, reject requests rather than return stale data.
- Examples: ZooKeeper, Etcd, Spanner, PostgreSQL (synchronous replication).

### Pros
- **Data integrity**: Users always see correct, up-to-date data.
- **Simple reasoning**: No stale data means no conflict resolution.
- **Financial safety**: Critical for banking, inventory, and booking systems.

### Cons
- **Reduced availability**: System may reject requests during partitions.
- **Higher latency**: Wait for quorum acknowledgment on writes.

## Availability (AP)

### Characteristics
- Every request receives a response (success or failure), but not guaranteed latest.
- During network partitions, continue serving potentially stale data.
- Examples: Cassandra, DynamoDB, CouchDB, Redis (async replication).

### Pros
- **Always available**: System continues operating during failures.
- **Low latency**: No need to wait for quorum acknowledgment.
- **User experience**: Users always get a response, even if slightly stale.

### Cons
- **Stale reads**: Users may see outdated data.
- **Conflict resolution**: Need merge strategies for concurrent writes.

## Decision Framework

| Factor | Choose CP When... | Choose AP When... |
|--------|------------------|------------------|
| Data criticality | Financial, inventory, bookings | Social feeds, preferences, logs |
| User expectation | Must see latest data | Slightly stale is acceptable |
| Partition frequency | Rare network issues | Frequent cross-region partitions |

## Staff-Level Insight

> "Partition tolerance is not optional. The real question is: when a partition occurs, do you reject requests (CP) or serve potentially stale data (AP)?"

- **Most systems are AP with CP hot paths**: Use AP for reads, CP for writes.
- **Staff insight**: Don't think of CAP as a system-wide choice. Use **per-operation consistency** — Cassandra and DynamoDB let you choose consistency level per query. Use `QUORUM` for writes (CP), `ONE` for reads (AP). This gives you the best of both: fast reads with correct writes.
