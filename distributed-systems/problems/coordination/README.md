# Coordination Primitives

Core distributed coordination mechanisms that enable multiple nodes to agree on shared state, elect leaders, and safely access shared resources.

## Problems (3)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Distributed Lock](distributed-lock/) | RedLock algorithm for coordinating access to shared resources | Redis SETNX, RedLock, TTL, clock drift, watchdog |
| [Leader Election](leader-election/) | Raft-based leader election for single-coordinator systems | Raft, majority quorum, split-brain prevention, term numbers |
| [Consistent Hashing](consistent-hashing/) | Distribute data across dynamic node sets with minimal movement | Hash ring, virtual nodes, rebalancing, load balancing |

## When to Use

- **Distributed Lock**: When multiple nodes must not execute the same critical section simultaneously (e.g., singleton job runners, cache-writer patterns).
- **Leader Election**: When exactly one node must coordinate a cluster-wide activity (e.g., Kafka controller, etcd leader, primary database writer).
- **Consistent Hashing**: When data must be partitioned across nodes that frequently join or leave (e.g., distributed cache, CDN edge nodes).

## Cross-References

- **Topics**: [Distributed Locks](../../distributed-locks/), [ZooKeeper](../../zookeeper/), [Consistency Models](../../consistency-models/)
- **Related**: [Distributed Config](../data-management/distributed-config/) often uses leader election for config push coordination.
