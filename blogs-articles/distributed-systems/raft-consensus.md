# Raft Consensus Algorithm

## Overview

Raft is a consensus algorithm for managing a replicated log. It was designed as an alternative to Paxos, with emphasis on understandability. Raft is used by Etcd, Consul, and CockroachDB for leader election and log replication.

## Three Sub-Problems

### 1. Leader Election
- Nodes start as **followers**
- If a follower doesn't receive heartbeats within the election timeout, it becomes a **candidate**
- Candidates request votes from peers; majority wins and becomes **leader**
- New election triggered if no leader is established

```
Follower → (timeout) → Candidate → (majority votes) → Leader
Leader → (heartbeat every 15ms) → Followers stay followers
```

### 2. Log Replication
- Leader accepts client requests and appends them to its log
- Leader replicates entries to followers in parallel
- Entry is **committed** when majority of nodes have it
- Leader applies committed entries to state machine

```
Client → Leader → [Log Entry] → Followers
                ← Ack ←
Committed when majority acknowledge
```

### 3. Safety
- **Election restriction**: Candidate must have up-to-date log to win election
- **Log matching**: If two entries have same index and term, they store same command
- **Leader completeness**: Once entry is committed, it exists in all future leaders' logs

## Key Concepts

### Terms
- Monotonically increasing numbers representing logical time
- Each term has at most one leader
- Used to detect stale leaders and resolve conflicts

### Commit Index
- Highest log entry known to be committed
- Only entries at or below commit index are applied to state machine

### Follower Consistency
- Leader maintains `nextIndex` and `matchIndex` for each follower
- On mismatch, leader decrements `nextIndex` and retries (entry truncation)

## Staff-Level Insights

### Election Timeout Tuning
- **Random timeout** (150-300ms) prevents split votes
- Too short: frequent elections on network blips
- Too long: slow failover when leader crashes
- **Staff insight**: Set election timeout based on your network latency. For local clusters, 150-300ms is fine. For cross-datacenter, increase to 1-3 seconds.

### Quorum Size
- **3 nodes**: Tolerate 1 failure, low latency
- **5 nodes**: Tolerate 2 failures, moderate latency
- **Avoid even numbers**: Creates ambiguity in majority
- **Staff insight**: Most production systems use **3-node clusters**. The marginal benefit of 5 nodes (tolerating 2 failures) rarely justifies the increased write latency and complexity.

### Raft vs Paxos
- **Raft**: Easier to understand and implement; leader-based; good for key-value stores
- **Paxos**: More flexible; multi-Paxos for high throughput; harder to reason about
- **Staff insight**: Use Raft for most consensus needs. Etcd and Consul prove it works at scale. Only consider Paxos if you need specific multi-Paxos optimizations.
