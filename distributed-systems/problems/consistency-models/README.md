# Consistency Models

## Overview

Consistency models define how data is replicated and when updates are visible across a distributed system. For staff engineers, consistency is not binary — it's a **spectrum** with trade-offs between latency, availability, and complexity.

## Models

### Strong Consistency
- All reads return the latest write
- **Linearizability**: Operations appear to execute instantaneously in some total order
- **Implementation**: Single writer, quorum-based reads/writes (R+W > N), distributed locks
- **Latency**: High — bounded by slowest replica or lock acquisition
- **Use case**: Financial transactions, inventory systems, seat booking
- **Staff insight**: True linearizability is expensive. Use **single-writer pattern** where possible — one service owns writes, others read, eliminating conflicts.

### Eventual Consistency
- Reads eventually return the latest write
- **Implementation**: Async replication, gossip protocols, anti-entropy
- **Latency**: Low — no wait for replication
- **Use case**: Social feeds, comments, likes, DNS, CDN
- **Staff insight**: Eventual consistency requires **conflict resolution** (LWW, FWW, custom merge). Design data models to minimize conflicts — use **append-only** structures where possible.

### Session Consistency
- Guarantees within a single session
- **Sub-properties**:
  - **Read-Your-Writes**: User always sees their own writes
  - **Monotonic Reads**: User never sees older data after a newer read
  - **Monotonic Writes**: User's writes are applied in order
- **Implementation**: Sticky sessions to same replica; route post-write reads to primary
- **Use case**: E-commerce carts, user profiles, editing workflows
- **Staff insight**: Session consistency is the **sweet spot** for most user-facing applications. It provides strong consistency where it matters (user's own data) without the cost of global strong consistency.

### Causal Consistency
- If operation B causally depends on operation A, B sees A's effects
- **Implementation**: Vector clocks, version vectors, dependency tracking
- **Use case**: Collaborative editing, chat threads, social media replies
- **Staff insight**: Causal consistency is hard to implement correctly. Use **vector clocks** to track causality. For simpler cases, **timestamp + version** often suffices.

## CAP Theorem

In a distributed system, you can only guarantee two of three:

| Property | Definition | Practical Meaning |
|----------|-----------|-------------------|
| **Consistency (C)** | All nodes see the same data at the same time | Linearizable reads; no stale data |
| **Availability (A)** | Every request receives a response | System always responds, even during partitions |
| **Partition Tolerance (P)** | System continues despite network partitions | Works when nodes can't communicate |

- **P is non-negotiable**: In distributed systems, network partitions will happen. You must choose between C and P.
- **CP systems**: Reject requests during partitions (e.g., ZooKeeper, HBase, Spanner)
- **AP systems**: Serve possibly stale data during partitions (e.g., Cassandra, DynamoDB)
- **Staff insight**: CAP is often misunderstood. The choice is **only during partitions**. In normal operation, you can have both C and A.

## Quorum-Based Consistency

- **Formula**: R + W > N (reads + writes > total nodes)
- **Example**: N=3, R=2, W=2 → strong consistency; N=3, R=1, W=2 → eventual consistency
- **Staff insight**: Tune R and W based on read/write ratio. Read-heavy? Increase R. Write-heavy? Increase W.

## Staff-Level Consistency Checklist

1. **Define consistency per operation**: Not all reads need strong consistency
2. **Use session consistency for user data**: Read-your-writes + monotonic reads
3. **Prefer eventual where possible**: Lower latency, higher availability
4. **Implement conflict resolution**: LWW, custom merge, or CRDTs for concurrent writes
5. **Use quorum-based reads/writes**: Tune R and W based on access patterns
6. **Monitor convergence time**: Track how long eventual consistency takes
7. **Test partition scenarios**: Verify system behavior during network splits
8. **Document consistency guarantees**: Make model explicit in API contracts

### Causal Consistency
- Preserves causal ordering
- Related operations ordered correctly

## Vector Clocks

- Track causality between events
- Detect concurrent modifications
- Used in DynamoDB

## Conflict Resolution

- Last-Write-Wins (LWW)
- First-Write-Wins (FWW)
- Custom merge functions
- CRDTs (Conflict-free Replicated Data Types)
