# Distributed Lock (RedLock)

## Problem Statement

Design a distributed lock service like Redis RedLock that allows multiple nodes in a distributed system to coordinate access to shared resources with safety and liveness guarantees.

**Reference**: AlgoMaster, ByteByteGo

## Requirements

### Functional Requirements
- **Acquire lock**: Obtain exclusive lock with key and TTL.
- **Release lock**: Release lock when done; auto-expire on TTL.
- **Renew lock**: Extend lock TTL for long-running operations.
- **Fairness**: Optional FIFO ordering for lock acquisition.
- **Watchdog**: Auto-renew lock while the holder is alive.

### Non-Functional Requirements
- **Safety**: At most one holder at any time (no two nodes hold the lock simultaneously).
- **Liveness**: No deadlocks; locks always eventually released.
- **Latency**: Lock acquisition < 10ms.

## Key Design Decisions
- **RedLock algorithm**: Acquire lock on N/2 + 1 of N independent Redis nodes.
- **TTL**: Lock auto-expires to prevent deadlock on holder crash.
- **Unique token**: Each lock has a random token; release only with matching token.
- **Clock drift handling**: Account for clock drift when calculating TTL.

## Staff-Level Design Considerations

### RedLock Algorithm
- **Quorum-based**: Write to N independent Redis nodes. If successful on N/2 + 1, lock is acquired.
- **Staff insight**: RedLock is controversial (Martin Kleppmann vs Salvatore Sanfilippo debate). For production, use Redis Cluster with a single master per key — simpler and safer. RedLock is only needed if you can't trust a single master.

### TTL and Clock Drift
- **Effective TTL**: TTL - clock_drift - acquisition_time. This ensures the lock expires before another node can acquire it.
- **Staff insight**: If your TTL is 10s and clock drift is 500ms, the effective safe hold time is 9.5s. If your operation takes longer, use a watchdog to renew the lock.
