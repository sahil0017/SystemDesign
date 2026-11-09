# Leader Election (Raft)

## Problem Statement

Design a leader election algorithm like Raft that ensures a single leader is elected from a cluster of nodes, handles leader failures, and maintains consistency in a distributed system.

**Reference**: AlgoMaster, ByteByteGo

## Requirements

### Functional Requirements
- **Leader election**: Elect a single leader from N nodes using majority vote.
- **Heartbeat**: Leader sends periodic heartbeats to maintain authority.
- **Failover**: Automatic re-election when leader fails.
- **Term-based**: Monotonically increasing terms to handle split-brain.
- **Log replication**: Leader replicates log entries to followers.

### Non-Functional Requirements
- **Safety**: At most one leader per term.
- **Liveness**: Election completes within seconds of leader failure.
- **Scale**: 5-7 node clusters (odd number for majority).

## Key Design Decisions
- **Majority quorum**: Leader needs votes from (N/2 + 1) nodes.
- **Random election timeout**: Prevents vote splitting when multiple nodes become candidates simultaneously.
- **Pre-vote**: Optional pre-vote phase to prevent disruptive elections from partitioned nodes.

## Staff-Level Design Considerations

### Raft vs Paxos
- **Raft**: Designed for understandability. Explicit leader, term-based, log replication.
- **Paxos**: More general but harder to implement correctly. Multi-Paxos is equivalent to Raft.
- **Staff insight**: Use Raft for new systems. It's well-understood, has reference implementations (etcd, Consul), and is easier to reason about.

### Split-Brain Prevention
- **Majority quorum**: With N=5, a leader needs 3 votes. Two partitions of 2 and 3 nodes — only the 3-node partition can elect a leader.
- **Staff insight**: Always use odd numbers of nodes (3, 5, 7). N=4 has the same fault tolerance as N=3 (1 failure) but requires 3 votes. N=5 tolerates 2 failures.
