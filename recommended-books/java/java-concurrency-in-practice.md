# Java Concurrency in Practice by Brian Goetz

## Summary

The definitive guide to Java concurrency. Covers the Java Memory Model, thread safety, composition, immutability, synchronization, executors, concurrent collections, and advanced topics like atomic variables and non-blocking algorithms.

## Key Chapters

1. **Thread Safety**: Correctness, visibility, atomicity, invariants
2. **Sharing Objects**: Immutability, thread confinement, synchronized programs
3. **Composing Objects**: Thread safety in classes, delegation, monitoring pattern
4. **Thread Pools and Tasks**: Executors, CompletableFuture, task cancellation
5. **Cancellation and Shutdown**: Interruptible tasks, poison pills, shutdown hooks
6. **Composition with Concurrency Utilities**: Blocking queues, concurrent collections
7. **Atomic Variables**: CAS, AtomicReference, LongAdder, StampedLock
8. **Explicit Locks**: ReentrantLock, ReadWriteLock, condition variables
9. **Advanced Topics**: Fork/Join, Phaser, non-blocking algorithms

## Key Takeaways

- **Immutability is the foundation**: Immutable objects are inherently thread-safe
- **Prefer high-level concurrency utilities**: Executors, concurrent collections, and atomic variables over raw threads and synchronized
- **Document thread safety**: Every class should declare its thread safety guarantees
- **Avoid shared mutable state**: Use thread confinement, immutability, or proper synchronization
- **Beware of livelock and starvation**: Design fair algorithms that don't starve threads

## Why Read This Book

- The definitive guide to Java concurrency — essential for understanding thread safety
- Covers both theory (JMM, happens-before) and practice (executors, concurrent collections)
- Required reading for any Java engineer working on concurrent systems

## Related Problems in This Repository

- [Java - Concurrency Problems](../../java/problems/)
- [Blogs - Java Memory Model](../../blogs-articles/java-concurrency/java-memory-model.md)
- [Blogs - Lock-Free Programming](../../blogs-articles/java-concurrency/lock-free.md)
