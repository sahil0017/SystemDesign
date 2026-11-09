# Blocking Queue Design

## Problem Statement

Design and implement a thread-safe blocking queue that supports blocking put and take operations, enabling efficient producer-consumer coordination with bounded capacity.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Blocking put**: Block when queue is full until space is available.
- **Blocking take**: Block when queue is empty until an element is available.
- **Non-blocking operations**: `offer`, `poll`, `peek` with optional timeout.
- **Bounded capacity**: Fixed maximum size to prevent unbounded memory growth.
- **Queue operations**: `size`, `isEmpty`, `iterator`, `drainTo`.

### Non-Functional Requirements
- **Thread safety**: Multiple producers and consumers can operate concurrently.
- **Fairness**: Optional FIFO ordering for waiting threads.
- **Performance**: Minimal lock contention; high throughput under concurrent access.

## Key Design Decisions
- **Array-based**: Circular array for bounded storage; better cache locality than linked nodes.
- **Two locks**: Separate `putLock` and `takeLock` for independent producer/consumer access.
- **Condition variables**: `notFull` condition for put; `notEmpty` condition for take.
- **Count**: `AtomicInteger` tracks current size for lock-free size check.

## Staff-Level Design Considerations

### Two-Lock Design
- **Put lock**: Protects put operations and the `notFull` condition.
- **Take lock**: Protects take operations and the `notEmpty` condition.
- **Why two locks**: Producers and consumers don't block each other; only compete for array access.
- **Staff insight**: Java's `ArrayBlockingQueue` uses this two-lock design. It allows a producer and consumer to operate simultaneously, doubling throughput compared to a single-lock design.

### Condition Variables
- **notFull**: Signaled when an element is removed; wakes waiting producers.
- **notEmpty**: Signaled when an element is added; wakes waiting consumers.
- **Signal vs signalAll**: Use `signal()` for fairness; `signalAll()` for non-fair mode.
- **Staff insight**: Using `signal()` instead of `signalAll()` reduces spurious wakeups and context switches. In fair mode, only the longest-waiting thread is woken.

### Blocking Queue Variants
- **ArrayBlockingQueue**: Bounded array; two locks; highest throughput for bounded queues.
- **LinkedBlockingQueue**: Optionally unbounded; separate put/take locks; node-based.
- **SynchronousQueue**: Direct handoff; no storage; each insert must wait for a remove.
- **PriorityBlockingQueue**: Unbounded priority queue; no blocking put.
- **Staff insight**: Choose ArrayBlockingQueue for bounded workloads with known capacity. Use LinkedBlockingQueue when you need optional unbounded behavior. Use SynchronousQueue for direct producer-consumer handoff (e.g., thread pool work queue).

### Common Pitfalls
- **Unbounded queue risk**: LinkedBlockingQueue with no bound can cause OOM under high production rate.
- **Deadlock**: Blocking put/take with improper timeout handling can deadlock.
- **Thread interruption**: Blocking operations throw InterruptedException; handle it properly.
- **Staff insight**: Always use bounded queues in production to prevent OOM. Set capacity based on your backpressure strategy — the queue size should be large enough to absorb bursts but small enough to trigger backpressure when the system is overwhelmed.
