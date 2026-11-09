# CAP Theorem in Practice

## Overview

The CAP theorem states that a distributed system can provide at most two of three guarantees: Consistency, Availability, and Partition Tolerance. This article explores what CAP means in real-world system design and how to make practical trade-off decisions.

## The Three Guarantees

### Consistency (C)
Every read receives the most recent write or an error. All nodes see the same data at the same time.

### Availability (A)
Every request receives a (non-error) response, without guarantee that it contains the most recent write.

### Partition Tolerance (P)
The system continues to operate despite network partitions between nodes.

## The Reality: You Must Choose P

In distributed systems, **network partitions will happen**. You cannot avoid them. Therefore, the real choice is between **CP** and **AP**.

### CP Systems (Consistency + Partition Tolerance)
- **Examples**: ZooKeeper, Etcd, MongoDB (default), PostgreSQL
- **Behavior during partition**: Reject reads/writes that can't guarantee consistency
- **Use cases**: Financial transactions, inventory management, user authentication
- **Trade-off**: System may become unavailable during partition but data is always correct

### AP Systems (Availability + Partition Tolerance)
- **Examples**: Cassandra, DynamoDB, Riak, DNS
- **Behavior during partition**: Continue serving potentially stale data
- **Use cases**: Social feeds, product catalogs, logging, analytics
- **Trade-off**: System stays available but may return stale or conflicting data

## Real-World Examples

### MongoDB (CP by Default)
- Writes to primary, secondaries replicate asynchronously
- During partition, if primary is isolated, new primary is elected
- Reads during partition may be rejected if consistency can't be guaranteed

### Cassandra (AP by Default)
- Writes to multiple replicas with configurable consistency level
- During partition, accepts writes on available nodes
- Uses **anti-entropy repair** (anti-entropy, read repair) to resolve conflicts
- Consistency levels: ONE, QUORUM, ALL — tune per operation

### DynamoDB (AP with Tunable Consistency)
- Default: Eventual consistency (AP)
- Optional: Strong consistency reads (CP-like)
- Uses **vector clocks** for conflict resolution

## Tunable Consistency

### Read/Write Consistency Levels
```
Cassandra consistency levels:
ONE       — Acknowledge from 1 replica
QUORUM    — Acknowledge from majority (N/2 + 1)
ALL       — Acknowledge from all replicas
```

### The W + R > N Rule
- **W**: Number of replicas that must acknowledge write
- **R**: Number of replicas that must respond to read
- **N**: Total number of replicas
- If **W + R > N**, you guarantee consistency (read overlaps with latest write)

## Staff-Level Insights

### CAP is a Spectrum
- Real systems don't fit neatly into CP or AP — they operate on a spectrum
- **PACELC extension**: When there is no partition (E), do you choose Latency or Consistency (L)?
- Design systems with **tunable consistency** — let each operation choose its level

### Design for Partitions
- Assume partitions will happen — design your system to handle them gracefully
- Use **read repair** and **anti-entropy** to eventually converge data
- Implement **conflict resolution** strategies (last-write-wins, custom merge functions)

### Choose Based on Domain
- **Financial systems**: CP — never serve stale balance data
- **Social feeds**: AP — stale posts are acceptable; availability matters more
- **Hybrid approach**: Use CP for critical data (payments), AP for non-critical (feeds)
- **Staff insight**: Don't pick one model for the entire system. Use **polyglot persistence** — different databases for different consistency needs.
