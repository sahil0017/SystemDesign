# Concurrency Fundamentals

## Problem Statement

Design a comprehensive understanding of Java concurrency fundamentals including thread lifecycle, synchronization primitives, memory model, and common concurrency patterns for building thread-safe applications.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Thread creation**: Extend `Thread` vs implement `Runnable` vs `Callable`.
- **Thread lifecycle**: NEW → RUNNABLE → RUNNING → BLOCKED/WAITING/TIMED_WAITING → TERMINATED.
- **Synchronization**: `synchronized` keyword for mutual exclusion and memory visibility.
- **Volatile keyword**: Guarantees visibility and ordering; prevents instruction reordering.
- **Thread communication**: `wait()`, `notify()`, `notifyAll()` for producer-consumer coordination.
- **Thread joining**: `join()` to wait for thread completion.
- **Daemon threads**: Background threads that don't prevent JVM shutdown.

### Non-Functional Requirements
- **Thread safety**: Correct behavior under concurrent access.
- **Performance**: Minimal synchronization overhead.
- **Deadlock freedom**: No circular lock dependencies.
- **Memory visibility**: Changes by one thread are visible to others.

## Key Design Decisions
- **Runnable over Thread**: Prefer composition over inheritance; allows task execution in thread pools.
- **Callable over Runnable**: Returns result and throws checked exceptions.
- **synchronized blocks**: Prefer block-level over method-level for finer-grained locking.
- **Volatile for flags**: Use `volatile` for simple flags and status variables; not for compound operations.

## Staff-Level Design Considerations

### Java Memory Model (JMM)
- **Happens-before relationship**: Defines when writes by one thread are visible to another.
  - Program order: Each action happens-before every action that follows it in program order.
  - Monitor lock: Unlock happens-before every subsequent lock on the same monitor.
  - Volatile: Write to volatile happens-before every subsequent read of the same volatile.
  - Thread start: `thread.start()` happens-before every action in the started thread.
  - Thread join: Every action in a thread happens-before `thread.join()` returns.
- **Staff insight**: Understanding JMM is critical for writing correct concurrent code. `volatile` alone doesn't guarantee atomicity — it only guarantees visibility and ordering.

### Synchronization Deep Dive
- **Intrinsic lock**: Every object has a monitor; `synchronized` acquires/releases it.
- **Reentrancy**: A thread can re-acquire a lock it already holds; lock has a counter.
- **Lock coarsening**: JVM may merge adjacent synchronized blocks for performance.
- **Lock elimination**: JIT may remove synchronization if escape analysis proves no sharing.
- **Staff insight**: `synchronized` is not just about mutual exclusion — it establishes a happens-before relationship that flushes CPU caches. Without it, threads may see stale values.

### Common Concurrency Bugs
- **Race condition**: Non-atomic read-modify-write on shared state. Fix: synchronize or use atomics.
- **Deadlock**: Circular lock dependency. Fix: acquire locks in consistent order; use `tryLock()`.
- **Livelock**: Threads actively respond to each other but make no progress. Fix: add random backoff.
- **Starvation**: Low-priority threads never get CPU. Fix: use fair locks or priority queues.
- **Memory visibility**: Thread sees stale values. Fix: use `volatile`, `synchronized`, or atomics.
- **False sharing**: Threads modify different fields on the same cache line. Fix: padding with `@Contended`.
- **Staff insight**: Most concurrency bugs are intermittent and hard to reproduce. Use stress testing tools like `jcstress` and code review to catch them early.

### Thread Best Practices
- **Use thread pools**: Never create threads manually in production; use `ExecutorService`.
- **Prefer high-level utilities**: `CompletableFuture`, `ConcurrentHashMap`, `BlockingQueue`.
- **Immutable objects**: Thread-safe by default; no synchronization needed.
- **Thread-local storage**: `ThreadLocal` for per-thread state; avoid memory leaks with `remove()`.
- **Staff insight**: The best concurrent code is code that doesn't share mutable state. Design for immutability first, then add synchronization only where necessary.
