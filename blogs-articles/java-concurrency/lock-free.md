# Lock-Free Programming

## Overview

Lock-free programming uses atomic operations (CAS — Compare-And-Swap) instead of locks for thread synchronization. It avoids deadlocks, reduces contention, and provides better scalability under high concurrency.

## CAS (Compare-And-Swap)

### How It Works
```java
AtomicInteger counter = new AtomicInteger(0);

// CAS operation: if current == expected, set to updated
boolean success = counter.compareAndSet(expected, updated);

// High-level operations built on CAS
counter.incrementAndGet();    // Loop CAS until success
counter.addAndGet(10);        // Loop CAS until success
```

### CAS Loop Pattern
```java
// incrementAndGet() implementation (simplified)
public final int incrementAndGet() {
    int current, next;
    do {
        current = get();
        next = current + 1;
    } while (!compareAndSet(current, next));  // Retry if CAS fails
    return next;
}
```

## The ABA Problem

### The Issue
```
Thread 1:  Reads value A, preps to change to B
Thread 2:  Changes A → B → A (value is A again)
Thread 1:  CAS succeeds (sees A), but state has changed!
```

### Solution: AtomicStampedReference
```java
AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(0, 0);
Integer value = ref.getReference();
int stamp = ref.getStamp();

// CAS with version stamp prevents ABA
ref.compareAndSet(value, newValue, stamp, stamp + 1);
```

## Atomic Variables

| Class | Purpose |
|-------|---------|
| AtomicInteger | Atomic int operations |
| AtomicLong | Atomic long operations |
| AtomicReference<T> | Atomic object reference |
| AtomicBoolean | Atomic boolean operations |
| AtomicIntegerFieldUpdater | Atomic update on existing fields |
| LongAdder | High-contentor counter (better than AtomicInteger) |

## LongAdder vs AtomicInteger

### AtomicInteger
- Single CAS variable
- High contention: threads compete for the same CAS variable
- Good for low-to-moderate contention

### LongAdder
- Splits counter into multiple cells (one per thread)
- Each thread updates its own cell — no contention
- `sum()` aggregates all cells
- **Better for high contention**

```java
// High-contention counter
LongAdder counter = new LongAdder();
counter.increment();
long sum = counter.sum();
```

## Lock-Free Data Structures

### ConcurrentLinkedQueue
- Lock-free queue using CAS on head/tail nodes
- Non-blocking offer() and poll()

### ConcurrentHashMap
- Uses CAS for node insertion
- Lock-free reads, fine-grained locking for writes

### Disruptor Pattern
- Ring buffer with CAS-based sequence management
- Used in high-performance systems (financial trading, logging)
- Avoids cache line bouncing with padding

## Staff-Level Insights

### When to Use Lock-Free
- **High contention**: Many threads competing for the same resource
- **Low latency**: Lock-free avoids thread suspension/resumption overhead
- **Deadlock avoidance**: No locks means no deadlocks
- **Staff insight**: Lock-free is harder to reason about. Use locks (ReentrantLock) for most cases; switch to lock-free only when profiling shows contention is the bottleneck.

### When NOT to Use Lock-Free
- **Complex operations**: Multi-step operations are hard to make atomic with CAS
- **Low contention**: Locks have less overhead when contention is low
- **Read-heavy**: ReadWriteLock often outperforms lock-free for read-heavy workloads
- **Staff insight**: CAS loops under high contention cause **CPU spinning** — threads repeatedly fail CAS and retry, consuming CPU. Use `LongAdder` for counters and `StampedLock` for read-heavy workloads instead of raw CAS.

### StampedLock (Java 8+)
```java
StampedLock lock = new StampedLock();

// Optimistic read — no locking, check validity later
long stamp = lock.tryOptimisticRead();
// ... read fields ...
if (lock.validate(stamp)) { /* data is consistent */ }

// Read lock — shared, multiple readers
stamp = lock.readLock();
try { /* read fields */ } finally { lock.unlockRead(stamp); }

// Write lock — exclusive
stamp = lock.writeLock();
try { /* write fields */ } finally { lock.unlockWrite(stamp); }
```
- **Staff insight**: `StampedLock`'s optimistic read mode is the fastest read path — no locking at all. Use it when writes are rare and you can recheck consistency. It's the basis of `ConcurrentHashMap`'s lock-free reads.
