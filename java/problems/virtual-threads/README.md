# Virtual Threads (Project Loom)

## Problem Statement

Understand and implement Java Virtual Threads (Project Loom, Java 21+) — lightweight threads managed by the JVM that enable massive concurrency for I/O-bound workloads. Virtual threads eliminate the need for reactive programming and complex async patterns by making blocking code scalable.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Virtual thread creation**: Create millions of lightweight threads without OS thread overhead.
- **Blocking I/O**: Blocking operations (network, file, DB) don't block carrier threads.
- **Thread-local support**: Virtual threads support ThreadLocal with limitations.
- **Pinning awareness**: Identify code that pins virtual threads to carrier threads.
- **Migration**: Migrate from reactive (CompletableFuture, Reactor) to virtual threads.

### Non-Functional Requirements
- **Throughput**: Handle 1M+ concurrent virtual threads on a single machine.
- **Memory**: Each virtual thread uses ~1KB stack (vs ~1MB for platform threads).
- **Scheduling**: JVM schedules virtual threads on a pool of carrier platform threads.

## Key Design Decisions
- **ForkJoinPool carrier**: Virtual threads run on common ForkJoinPool by default.
- **Unmounting**: When virtual thread blocks, JVM unmounts it from carrier thread.
- **Mounting**: When I/O completes, JVM remounts virtual thread on any available carrier.
- **Scoped threads**: Java 21+ `Thread.ofVirtual().start()` for simple virtual threads.

## Implementation

```java
// Traditional platform thread (expensive)
ExecutorService platformExec = Executors.newFixedThreadPool(100);

// Virtual threads (massively scalable)
ExecutorService virtualExec = Executors.newVirtualThreadPerTaskExecutor();

// Blocking code that scales to millions of concurrent requests
virtualExec.submit(() -> {
    // This blocks the virtual thread, NOT the carrier thread
    var response = httpClient.send(request, BodyHandlers.ofString());
    processResponse(response);
});

// Structured concurrency with virtual threads
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User> user = scope.fork(() -> fetchUser(userId));
    Subtask<Order> order = scope.fork(() -> fetchOrder(orderId));
    scope.join().throwIfFailed();
    process(user.get(), order.get());
}
```

## Staff-Level Design Considerations

### Virtual Threads vs Platform Threads
- **Platform threads**: 1:1 mapping to OS threads; ~1MB stack; expensive to create.
- **Virtual threads**: M:N mapping to carrier threads; ~1KB stack; cheap to create.
- **Staff insight**: Use **virtual threads for I/O-bound workloads** (HTTP servers, DB calls, API clients). Use **platform threads for CPU-bound workloads** (computation, image processing). Virtual threads don't help CPU-bound tasks — they still need carrier threads.

### Pinning Problem
- **Pinning**: When virtual thread holds a monitor (`synchronized`), it can't unmount from carrier.
- **Impact**: Pinning exhausts carrier threads, defeating the purpose of virtual threads.
- **Staff insight**: **Replace `synchronized` with `ReentrantLock`** in code that runs on virtual threads. `ReentrantLock` doesn't pin — the lock wait is interruptible and unmountable. Profile with `-Djdk.tracePinnedThreads=short` to find pinning hotspots. This is the #1 gotcha with virtual threads.

### Migration from Reactive
- **Reactive (Reactor/RxJava)**: Non-blocking, backpressure, complex operator chains.
- **Virtual threads**: Blocking code, simple control flow, no backpressure built-in.
- **Staff insight**: **Migrate web servers to virtual threads** — replace Netty/Reactor with Tomcat on virtual threads. Code becomes simpler: blocking HTTP calls instead of reactive chains. For backpressure, use **semaphores** or **bounded queues** explicitly. Virtual threads simplify code 10x but require explicit flow control.

### ThreadLocal with Virtual Threads
- **InheritableThreadLocal**: Virtual threads inherit values at creation, not at scheduling.
- **Memory leak risk**: ThreadLocal values leak if not cleaned up in long-lived virtual threads.
- **Staff insight**: **Avoid ThreadLocal with virtual threads** where possible. Use explicit parameters or `ThreadLocal.withInitial()`. If you must use ThreadLocal, clean up in `finally` block. For request context, use **explicit context passing** instead of ThreadLocal — virtual threads are created per-request, so inheritance works, but cleanup is critical.
