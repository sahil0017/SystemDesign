# Consistency

## Overview

Consistency defines how data is replicated and when updates are visible across a distributed system. For staff engineers, consistency is not binary — it's a **spectrum** with trade-offs between latency, availability, and complexity. Choosing the right consistency model is one of the most impactful architectural decisions.

## CAP Theorem

In a distributed system, you can only guarantee two of three:

| Property | Definition | Practical Meaning |
|----------|-----------|-------------------|
| **Consistency (C)** | All nodes see the same data at the same time | Linearizable reads; no stale data |
| **Availability (A)** | Every request receives a response (success/failure) | System always responds, even during partitions |
| **Partition Tolerance (P)** | System continues operating despite network partitions | Works when nodes can't communicate |

### Key Insights
- **P is non-negotiable**: In distributed systems, network partitions will happen. You must choose between C and P.
- **CP systems**: Reject requests during partitions (e.g., ZooKeeper, HBase, Spanner)
- **AP systems**: Serve possibly stale data during partitions (e.g., Cassandra, DynamoDB, CouchDB)
- **Staff insight**: CAP is often misunderstood. The choice is **only during partitions**. In normal operation, you can have both C and A. The real question is: **what happens during a network partition?**

## PACELC Theorem

Extension of CAP that addresses the non-partition case:

| Condition | Trade-off | Example |
|-----------|-----------|---------|
| **P**artition occurs | Choose **C**onsistency or **A**vailability | CP: Spanner; AP: Cassandra |
| **EL**se (no partition) | Choose **L**atency or **C**onsistency | Low latency: eventual consistency; Low latency + consistency: sync replication |

- **Staff insight**: PACELC is more practical than CAP. Even without partitions, you trade latency for consistency. **Sync replication** gives consistency at the cost of latency; **async replication** gives low latency with eventual consistency.

## Consistency Models (Spectrum)

### Strong Consistency (Linearizability)
- **Definition**: All reads return the latest write; operations appear to execute instantaneously in some total order
- **Implementation**: Single writer, quorum-based reads/writes (R+W > N), distributed locks
- **Latency**: High — bounded by slowest replica or lock acquisition
- **Use case**: Financial transactions, inventory systems, seat booking
- **Staff insight**: True linearizability is expensive. Use **single-writer pattern** where possible — one service owns writes, others read, eliminating conflicts.

### Sequential Consistency
- **Definition**: All operations appear in some total order; each process sees operations in program order
- **Weaker than**: Linearizability (doesn't require real-time ordering)
- **Use case**: Distributed databases with ordered logs
- **Staff insight**: Sequential consistency is sufficient for most applications. Linearizability is overkill unless you need real-time correctness.

### Eventual Consistency
- **Definition**: If no new updates are made, all replicas will eventually converge to the same value
- **Implementation**: Async replication, gossip protocols, anti-entropy
- **Latency**: Low — no wait for replication
- **Use case**: Social feeds, comments, likes, DNS, CDN
- **Staff insight**: Eventual consistency requires **conflict resolution** (LWW, FWW, custom merge). Design data models to minimize conflicts — use **append-only** structures where possible.

### Session Consistency
- **Definition**: Guarantees consistency within a single user session
- **Sub-properties**:
  - **Read-Your-Writes**: User always sees their own writes
  - **Monotonic Reads**: User never sees older data after a newer read
  - **Monotonic Writes**: User's writes are applied in order
- **Implementation**: Sticky sessions to same replica; route post-write reads to primary
- **Use case**: E-commerce carts, user profiles, editing workflows
- **Staff insight**: Session consistency is the **sweet spot** for most user-facing applications. It provides strong consistency where it matters (user's own data) without the cost of global strong consistency.

### Causal Consistency
- **Definition**: If operation B causally depends on operation A, B sees A's effects
- **Implementation**: Vector clocks, version vectors, dependency tracking
- **Use case**: Collaborative editing, chat threads, social media replies
- **Staff insight**: Causal consistency is hard to implement correctly. Use **vector clocks** to track causality. For simpler cases, **timestamp + version** often suffices.

## Consensus Algorithms

### Raft
- **How it works**: Leader-based consensus; log replication; election on leader failure
- **Properties**: Strong consistency; fault tolerance (N/2+1 quorum)
- **Implementation**: etcd, Consul, CockroachDB, TiKV
- **Staff insight**: Raft is the **default choice** for new consensus needs. It's easier to understand and implement than Paxos. Use existing Raft implementations (etcd, Consul) rather than building your own.

### Paxos
- **How it works**: Multi-instance consensus; proposer, acceptor, learner roles
- **Properties**: Strong consistency; handles network partitions
- **Implementation**: Google Chubby, Spanner (Multi-Paxos)
- **Staff insight**: Paxos is proven but complex. **Multi-Paxos** (stable leader) is what's used in production. Prefer Raft for new projects.

### ZAB (ZooKeeper Atomic Broadcast)
- **How it works**: Combines leader election with atomic broadcast
- **Implementation**: Apache ZooKeeper
- **Staff insight**: ZAB is ZooKeeper-specific. For new projects, consider **etcd** (Raft-based) as a more modern alternative.

## Practical Consistency Patterns

### Quorum-Based Consistency
- **Formula**: R + W > N (reads + writes > total nodes)
- **Example**: N=3, R=2, W=2 → strong consistency; N=3, R=1, W=2 → eventual consistency
- **Staff insight**: Tune R and W based on read/write ratio. Read-heavy? Increase R. Write-heavy? Increase W.

### Read Repair
- **How it works**: On read, if replicas differ, repair the stale ones in background
- **Use case**: Cassandra, DynamoDB
- **Staff insight**: Read repair provides **self-healing** consistency. Combine with **anti-entropy** background processes for full convergence.

### Version Vectors & Conflict Resolution
- **How it works**: Each replica maintains version vector; detect concurrent modifications
- **Resolution**: Last-write-wins (LWW), first-write-wins (FWW), custom merge, CRDTs
- **Staff insight**: **CRDTs** (Conflict-free Replicated Data Types) eliminate conflicts by design. Use for counters, sets, and documents where convergence is critical.

## Staff-Level Consistency Checklist

1. **Define consistency requirements per operation**: Not all reads need strong consistency
2. **Use session consistency for user-facing data**: Read-your-writes + monotonic reads
3. **Prefer eventual consistency where possible**: Lower latency, higher availability
4. **Implement conflict resolution**: LWW, custom merge, or CRDTs for concurrent writes
5. **Use quorum-based reads/writes**: Tune R and W based on access patterns
6. **Monitor convergence time**: Track how long eventual consistency takes in production
7. **Test partition scenarios**: Verify system behavior during network splits
8. **Document consistency guarantees**: Make consistency model explicit in API contracts
