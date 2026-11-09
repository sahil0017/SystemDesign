# Virtual Threads (Project Loom)

## Overview

Virtual threads (Java 21+) are lightweight threads managed by the JVM rather than the OS. They enable massive concurrency for I/O-bound applications without the complexity of reactive programming.

## Platform Threads vs Virtual Threads

### Platform Threads
- 1:1 mapping to OS threads
- Expensive: ~1MB stack size per thread
- Limited: ~10,000 threads before running out of memory
- Context switch: OS-level, expensive

### Virtual Threads
- M:N mapping: Many virtual threads on few carrier threads
- Cheap: Stack starts at ~KB, grows as needed
- Unlimited: Millions of virtual threads on hundreds of carrier threads
- Context switch: JVM-level, cheap; only on blocking operations

## How It Works

```java
// Create virtual thread
Thread.startVirtualThread(() -> {
    // I/O operation — blocks virtual thread, NOT carrier thread
    var data = httpClient.send(request);
    // Resumes on a carrier thread when I/O completes
    process(data);
});

// Virtual thread pool
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> handleRequest(i));
    }
}
```

### Pinning Problem
- Virtual thread is **pinned** to carrier thread when holding a lock during blocking I/O
- Pinning prevents the carrier thread from running other virtual threads
- **Solution**: Avoid holding locks during I/O; use `java.util.concurrent` locks (ReentrantLock) over `synchronized`

## When to Use Virtual Threads

### Good Fit
- **I/O-bound services**: Web servers, API clients, database access
- **High concurrency**: 10K+ concurrent requests
- **Thread-per-request** pattern: Simplifies code without reactive complexity

### Bad Fit
- **CPU-bound tasks**: No benefit; limited by carrier thread count
- **Lock-heavy code**: Pinning negates benefits
- **Legacy code with synchronized blocks**: May need refactoring

## Staff-Level Insights

### Structured Concurrency
- Java 21+ provides **StructuredTaskScope** for managing virtual thread lifecycles
- All child threads must complete before scope exits
- Exceptions from any child are propagated to the parent

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User> user = scope.fork(() -> findUser());
    Subtask<List<Order>> orders = scope.fork(() -> findOrders());
    scope.join().throwIfFailed();
    return new OrderConfirmation(user.get(), orders.get());
}
```

### Migration Strategy
- Replace `ThreadPoolExecutor` with `Executors.newVirtualThreadPerTaskExecutor()`
- Test for **pinning** — profile with `-Djdk.tracePinnedThreads=short`
- **Staff insight**: Virtual threads work best with **non-blocking I/O libraries**. If your code holds `synchronized` locks during I/O, fix the pinning first before expecting performance gains.

### Performance Comparison
| Approach | Throughput (req/s) | Complexity | Memory |
|----------|-------------------|------------|--------|
| Platform threads | ~1,000 | Low | High |
| Reactive (CompletableFuture) | ~50,000 | High | Low |
| Virtual threads | ~50,000 | Low | Low |

- **Staff insight**: Virtual threads give you reactive-level throughput with imperative code complexity. This is the killer feature — no more callback hell or reactive streams for I/O-bound services.
