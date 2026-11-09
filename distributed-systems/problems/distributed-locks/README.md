# Distributed Locks

## Overview

Distributed locks coordinate access to shared resources across multiple processes. For staff engineers, distributed locks are a **last resort** — they add latency, complexity, and failure modes. Prefer **idempotent operations** and **optimistic locking** when possible.

## Implementations

### Redis-based
- **SETNX** (SET if Not eXists): Simple lock with TTL
- **Redlock algorithm**: Multi-node Redis (5 nodes, majority quorum) for HA
- **Redisson library**: Java client with reentrant locks, lease renewal, watchdog
- **Staff insight**: Use **Redlock** for HA, but it's controversial — accepts brief lock violations. For strong guarantees, prefer ZooKeeper.

### ZooKeeper-based
- **Sequential ephemeral nodes**: Create node; check if lowest sequence; watch previous
- **Watch mechanism**: Notify when previous node is deleted (lock released)
- **Strong consistency**: Linearizable; no split-brain
- **Staff insight**: ZooKeeper provides **stronger guarantees** than Redis. Use when correctness matters more than latency.

### Database-based
- **SELECT FOR UPDATE**: Pessimistic locking; holds row lock until commit
- **Unique constraint**: Optimistic locking; conflict detection on insert/update
- **Staff insight**: Use for **low-contention** locks. For high contention, use Redis/ZooKeeper to avoid DB connection exhaustion.

## Key Design Decisions

### Lock Timeout
- **TTL**: Lock auto-releases after TTL to prevent deadlocks on crash
- **Watchdog**: Background thread renews TTL while lock holder is alive
- **Staff insight**: Always set TTL. Without it, a crashed holder creates a **permanent deadlock**.

### Lock Release
- **Atomic check-and-delete**: Only release if you still hold the lock
- **Lua script**: Atomic operation in Redis to prevent race conditions
- **Staff insight**: Never use simple DEL — another service may have acquired the lock after your TTL expired.

## Staff-Level Distributed Locks Checklist

1. **Prefer lock-free designs**: Idempotent operations, optimistic locking, queue-based processing
2. **Always set TTL**: Prevent deadlocks on holder crash
3. **Use atomic release**: Check-and-delete to prevent releasing another's lock
4. **Handle lock acquisition failure**: Retry with exponential backoff; circuit breaker
5. **Monitor lock contention**: High contention indicates design problem
6. **Use watchdog for long operations**: Renew TTL while processing
7. **Consider lease-based designs**: Instead of locks, use leases with automatic renewal
8. **Test failure scenarios**: Holder crash, network partition, clock skew
- Lease-based

## Challenges

- Lock timeout and renewal
- Split-brain scenarios
- Performance overhead
- Deadlock detection

## Best Practices

- Always set timeout
- Use lease-based locks
- Implement lock renewal
- Handle network partitions
