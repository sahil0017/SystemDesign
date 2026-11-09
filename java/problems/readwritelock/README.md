# ReadWriteLock

## Problem Statement

Implement a custom ReadWriteLock that allows multiple concurrent readers or a single exclusive writer.

**Reference**: AlgoMaster

## Requirements
- **Shared read lock**: Multiple threads can hold read lock simultaneously.
- **Exclusive write lock**: Only one thread can hold write lock; blocks all readers and writers.
- **Fairness**: Optional fair mode where locks are granted in FIFO order.

## Key Design Decisions
- **Readers count**: Atomic counter for active readers.
- **Writer flag**: Boolean flag for active writer.
- **Reentrancy**: Support reentrant read and write locks.

## Staff-Level Design Considerations
- **Writer starvation**: Without fairness, writers can starve if readers are continuous. Use a turn-based approach or queue.
- **Staff insight**: Java's `ReentrantReadWriteLock` uses a CLH lock queue. For fair mode, it tracks waiting writers and blocks new readers if any writer is waiting. This prevents writer starvation.
