# StampedLock (Optimistic Read Lock)

## Problem Statement

Implement and understand Java's `StampedLock` (Java 8+) — a read-write lock that adds optimistic read mode for lock-free reads. StampedLock outperforms ReadWriteLock when reads dominate and writes are rare, by allowing readers to proceed without acquiring a lock and validating afterward.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Read lock**: Exclusive read lock similar to ReadWriteLock read lock.
- **Write lock**: Exclusive write lock similar to ReadWriteLock write lock.
- **Optimistic read**: Lock-free read that validates with a stamp afterward.
- **Stamp validation**: Check if optimistic read stamp is still valid.
- **Conversion**: Convert read lock to write lock without releasing.

### Non-Functional Requirements
- **Performance**: Optimistic reads should have zero contention under read-heavy load.
- **Non-reentrant**: StampedLock is not reentrant — each acquire returns a new stamp.
- **Non-interruptible**: Lock acquisition doesn't respond to interrupts.

## Key Design Decisions
- **Optimistic mode**: Reader gets a stamp without blocking; validates after read.
- **Stamp**: Long value representing lock state; used for validation and release.
- **Conversion**: Read-to-write conversion avoids release-acquire race window.

## Implementation

```java
public class Point {
    private double x, y;
    private final StampedLock lock = new StampedLock();

    // Optimistic read (lock-free)
    public double distanceFromOrigin() {
        long stamp = lock.tryOptimisticRead();
        double currentX = x, currentY = y;
        if (!lock.validate(stamp)) {
            stamp = lock.readLock();
            try {
                currentX = x;
                currentY = y;
            } finally {
                lock.unlockRead(stamp);
            }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }

    // Write lock
    public void move(double deltaX, double deltaY) {
        long stamp = lock.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            lock.unlockWrite(stamp);
        }
    }

    // Read-to-write conversion
    public void moveIfAtOrigin(double newX, double newY) {
        long stamp = lock.readLock();
        try {
            if (x == 0.0 && y == 0.0) {
                long writeStamp = lock.tryConvertToWriteLock(stamp);
                if (writeStamp != 0L) {
                    x = newX;
                    y = newY;
                    lock.unlockWrite(writeStamp);
                    return;
                }
                lock.unlockRead(stamp);
                stamp = lock.writeLock();
                x = newX;
                y = newY;
            }
        } finally {
            if (stamp != 0L) {
                lock.unlockRead(stamp);
            }
        }
    }
}
```

## Staff-Level Design Considerations

### Optimistic Read Pattern
- **Try optimistic**: Get stamp without blocking — fast path.
- **Read data**: Read fields without holding any lock.
- **Validate**: Check if any write occurred during read — if valid, done.
- **Fallback**: If invalid, acquire read lock and re-read — slow path.
- **Staff insight**: Optimistic reads work when **writes are rare and reads are fast**. If writes are frequent, `validate()` fails often, and you pay the cost of both optimistic and locked read. Profile the validation failure rate — if >20%, use regular read lock instead.

### StampedLock vs ReadWriteLock
- **ReadWriteLock**: Multiple readers or single writer; reentrant; interruptible.
- **StampedLock**: Optimistic reads + read/write; non-reentrant; non-interruptible.
- **Staff insight**: Use **StampedLock for read-heavy data structures** where optimistic reads succeed most of the time (e.g., configuration cache, reference data). Use **ReadWriteLock when you need reentrancy** or interruptible lock acquisition. Never use StampedLock in code that might call back into the lock from within a locked section.

### Common Pitfalls
- **Non-reentrant**: Calling `readLock()` from within a `readLock()` section deadlocks.
- **Stamp management**: Each lock mode has its own unlock method — mixing them throws.
- **Forgotten unlock**: Always use try-finally to release stamps.
- **Staff insight**: **Always use try-finally** with StampedLock. The stamp is just a long — if an exception occurs between `readLock()` and `unlockRead()`, the lock is leaked. Use a helper method or wrapper class to reduce boilerplate. Consider using `tryLock()` with timeout instead of blocking `readLock()`/`writeLock()` to prevent thread starvation.

### Read-Write-Read Pattern
- **Problem**: Need to read, then write conditionally, then read again.
- **Solution**: Use conversion — read lock → convert to write → unlock write.
- **Staff insight**: Conversion eliminates the **TOCTOU race** (time-of-check-time-of-use). Without conversion, releasing read lock and acquiring write lock creates a window where another thread can modify data. Conversion is atomic: if no other writer is waiting, it succeeds immediately. This is critical for lock-free data structures.
