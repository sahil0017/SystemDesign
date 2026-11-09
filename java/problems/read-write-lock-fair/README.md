# Read-Write Lock with Fairness

## Problem Statement

Design and implement a fair `ReadWriteLock` that allows multiple concurrent readers but exclusive access for writers, with a fairness policy to prevent writer starvation.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Multiple readers**: Multiple threads can hold read locks simultaneously.
- **Exclusive writer**: Only one writer can hold the write lock; no readers allowed during write.
- **Fairness policy**: First-come-first-served; waiting writers block new readers to prevent starvation.
- **Lock upgrade/downgrade**: Reader can upgrade to writer (with restrictions); writer can downgrade to reader.
- **TryLock with timeout**: Non-blocking attempt to acquire lock with timeout.
- **Condition support**: `newCondition()` for wait/notify patterns.

### Non-Functional Requirements
- **Thread safety**: All operations are thread-safe.
- **Deadlock freedom**: No self-deadlock on fair lock acquisition.
- **Performance**: Minimal overhead for read-heavy workloads.
- **Scalability**: Support high reader concurrency without contention.

## Key Design Decisions
- **State variable**: Single integer tracks read count and write count.
  - High 16 bits: write hold count
  - Low 16 bits: read count
- **Wait queue**: FIFO queue for fair ordering of readers and writers.
- **Writer preference**: When a writer is waiting, new readers are blocked to prevent writer starvation.
- **Reentrancy**: Same thread can re-acquire read or write lock; track hold count.

## Staff-Level Design Considerations

### Fairness vs Performance
- **Fair lock**: Guarantees ordering but adds overhead (queue management, context switches).
- **Non-fair lock**: Better throughput; allows readers to "barging" ahead of waiting writers.
- **Staff insight**: Use fair locks only when writer starvation is a real concern. In most read-heavy scenarios, non-fair locks provide better throughput. Java's `ReentrantReadWriteLock` defaults to non-fair.

### Lock Upgrade and Downgrade
- **Lock downgrade (safe)**: Writer can acquire read lock, then release write lock. This is safe because the write lock guarantees exclusive access.
  ```java
  writeLock.lock();
  try {
      // modify data
      readLock.lock();  // acquire read lock before releasing write
  } finally {
      writeLock.unlock();  // release write; still hold read
  }
  // read with read lock
  readLock.unlock();
  ```
- **Lock upgrade (unsafe)**: Reader cannot safely upgrade to writer. Other readers may be active, so acquiring write lock would deadlock.
- **Staff insight**: Lock downgrade is a common pattern for caching — write to update, then read from the cache with a read lock. Never attempt lock upgrade.

### Implementation Details
- **ReadersWriterLock state**: Use `AtomicInteger` or `synchronized` block for state management.
- **Queue management**: Use `java.util.concurrent.locks.AbstractQueuedSynchronizer` (AQS) as the foundation.
- **Condition variables**: Each lock can have multiple conditions for fine-grained wait/notify.
- **Staff insight**: Java's `ReentrantReadWriteLock` uses AQS with a custom sync implementation. Understanding AQS is key to building custom synchronizers.

### Common Pitfalls
- **Writer starvation**: Non-fair locks can starve writers in read-heavy workloads.
- **Read lock held too long**: Long read operations block writers indefinitely.
- **Deadlock on upgrade**: Attempting to upgrade from read to write lock will deadlock.
- **Hold read lock during I/O**: Blocks all writers; keep read lock scope minimal.
- **Staff insight**: Profile lock contention with JFR. If writers are starved, switch to fair mode or redesign to reduce read lock scope. Consider `StampedLock` for optimistic reads.
