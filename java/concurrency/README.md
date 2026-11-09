# Java Concurrency

## Overview

Java concurrency covers multi-threading and concurrent programming concepts. For staff engineers, concurrency is about **correctness under contention**, **performance under load**, and **avoiding subtle bugs** (deadlocks, race conditions, memory visibility).

## Core Concepts

- **Thread lifecycle and states**: NEW → RUNNABLE → RUNNING → BLOCKED/WAITING → TERMINATED
- **Synchronization**: `synchronized` keyword for mutual exclusion and memory visibility
- **volatile keyword**: Guarantees visibility across threads; prevents instruction reordering; no atomicity
- **synchronized blocks and methods**: Intrinsic lock; mutual exclusion; happens-before relationship
- **Thread pools (ExecutorService)**: Manage thread lifecycle; control concurrency; avoid thread creation overhead
- **CompletableFuture**: Async programming with callbacks; chain operations; compose results
- **Concurrent collections**: Thread-safe alternatives to standard collections
- **Atomic classes**: Lock-free thread-safe operations using CAS (Compare-And-Swap)
- **Locks (ReentrantLock, ReadWriteLock)**: Explicit locking with tryLock, fairness, condition variables
- **CountDownLatch, CyclicBarrier, Semaphore**: Coordination primitives for thread synchronization

## Common Issues

- **Deadlock**: Two threads waiting for each other's locks → circular dependency
- **Race conditions**: Non-atomic read-modify-write on shared mutable state
- **Thread starvation**: Low-priority threads never get CPU time
- **Livelock**: Threads actively respond to each other but make no progress
- **Memory visibility**: Thread-local caches may not see updates from other threads
- **False sharing**: Multiple threads modify different fields on same cache line

## Best Practices

1. **Prefer high-level utilities**: ExecutorService, CompletableFuture over raw threads
2. **Use immutable objects**: Thread-safe by default; no synchronization needed
3. **Minimize shared state**: Pass data via method parameters; avoid shared mutable state
4. **Use thread-safe collections**: ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
5. **Avoid synchronized blocks**: Prefer ReentrantLock with tryLock for timeout support
6. **Use try-finally for locks**: Always release locks in finally block
7. **Profile before optimizing**: Use JFR, JMC to identify actual bottlenecks
8. **Test with stress tests**: Use jcstress for concurrency bug detection

## Staff-Level Concurrency Checklist

1. **Prefer immutability**: Immutable objects are inherently thread-safe
2. **Use CompletableFuture for async**: Chain operations; handle exceptions; compose results
3. **Avoid busy-waiting**: Use wait/notify, CountDownLatch, or CompletableFuture
4. **Use thread pools**: Control concurrency; avoid thread creation overhead
5. **Profile before optimizing**: Identify actual bottlenecks with JFR/JMC
6. **Test under contention**: Stress test with multiple threads; use jcstress
7. **Avoid deadlocks**: Acquire locks in consistent order; use tryLock with timeout
8. **Document thread safety**: Make concurrency guarantees explicit in API docs

- Prefer high-level concurrency utilities
- Use immutable objects where possible
- Minimize shared mutable state
- Use thread-safe collections

## Problems (6)

| Problem | Key Concepts |
|---------|-------------|
| [Deadlock Detector](problems/deadlock-detector/) | Wait-for graph, DFS cycle detection, lock ordering |
| [Thread-Safe Singleton](problems/thread-safe-singleton/) | Bill Pugh, enum, double-checked locking, volatile |
| [Event Loop Design](problems/event-loop/) | Selector, task queue, non-blocking I/O |
| [Work Stealing Pool](problems/work-stealing-pool/) | Per-thread deque, CAS, fork/join pattern |
| [Read-Write Cache](problems/read-write-cache/) | StampedLock, optimistic reads, segmented cache |
| [Async Pipeline Design](problems/async-pipeline/) | Stage chaining, backpressure, per-stage executor |
