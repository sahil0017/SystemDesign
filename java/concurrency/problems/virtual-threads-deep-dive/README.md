# Virtual Threads Deep Dive (Java 21+)

## Problem Statement

Deep dive into Java 21 virtual threads (Project Loom), understanding how they work, when to use them, migration patterns from reactive programming, and performance implications for high-throughput server applications.

**Reference**: Java 21 JEP 444, Project Loom, Effective Java (3rd Edition)

## Requirements

### Learning Objectives
- **Virtual threads**: Understand how virtual threads differ from platform threads.
- **ForkJoinPool.common**: How virtual threads use the carrier thread pool.
- **Pinning**: Identify when virtual threads get pinned to carrier threads.
- **Migration from reactive**: Convert Reactor/WebFlux code to virtual threads.
- **Performance tuning**: Benchmark and tune virtual thread applications.

### Key Concepts
- **M:N scheduling**: M virtual threads scheduled onto M carrier (platform) threads.
- **Mounting/unmounting**: Virtual threads are mounted (running) and unmounted (blocked).
- **Structured concurrency**: Group related virtual threads as a single unit of work.
- **Synchronization**: How synchronized blocks and locks affect virtual threads.

## Code Examples

### Virtual Threads vs Platform Threads

```java
// Before: Platform thread pool (expensive, limited size)
ExecutorService platformPool = Executors.newFixedThreadPool(100);
platformPool.submit(() -> {
    Thread.sleep(1000); // Blocks a platform thread for 1 second
});

// After: Virtual threads (cheap, millions possible)
ExecutorService virtualPool = Executors.newVirtualThreadPerTaskExecutor();
virtualPool.submit(() -> {
    Thread.sleep(1000); // Virtual thread unmounts; carrier thread is free
});

// Try-finally with structured concurrency (Java 21 preview)
try (var scope = new StructTaskScope<Void>() {
    scope.fork(() -> fetchData());
    scope.fork(() -> fetchUser());
    scope.join(); // Wait for all subtasks
    scope.throwIfFailed();
}
```

### Migration from Reactive to Virtual Threads

```java
// Before: Reactive (WebFlux/Reactor)
public Mono<User> getUserWithOrders(String userId) {
    return userRepository.findById(userId)
        .flatMap(user -> orderRepository.findByUserId(user.getId())
            .map(orders -> new UserWithOrders(user, orders)));
}

// After: Virtual threads (synchronous style)
public UserWithOrders getUserWithOrders(String userId) {
    User user = userRepository.findById(userId);
    List<Order> orders = orderRepository.findByUserId(user.getId());
    return new UserWithOrders(user, orders);
}
// Called with: executor.submit(() -> getUserWithOrders(userId))
```

### Pinning Avoidance

```java
// BAD: Synchronized block pins virtual thread to carrier thread
synchronized (lock) {
    // Virtual thread cannot unmount while holding this lock
    Thread.sleep(1000); // Carrier thread is blocked!
}

// GOOD: Use ReentrantLock (virtual thread can unmount while waiting)
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // Virtual thread can unmount if it blocks inside the critical section
    doWork();
} finally {
    lock.unlock();
}

// GOOD: Use var handles or StampedLock for lock-free patterns
```

## Staff-Level Design Considerations

### When to Use Virtual Threads
- **I/O-bound workloads**: Web servers, database clients, API calls — where threads spend most time blocked.
- **High concurrency**: Millions of concurrent requests with simple synchronous code.
- **Migration from reactive**: Replace complex reactive pipelines with simple synchronous code.
- **Staff insight**: Virtual threads are a game-changer for I/O-bound servers. A single machine can handle 1M+ concurrent requests with virtual threads, vs ~10K with platform threads. Use them for all new I/O-bound services.

### Pinning — The #1 Pitfall
- **What causes pinning**: `synchronized` blocks, `BlockingQueue.take()`, and native method calls.
- **Impact**: A pinned virtual thread blocks its carrier thread, reducing throughput.
- **Detection**: Use `-Djdk.tracePinnedThreads=short` to detect pinned threads.
- **Staff insight**: Pinning is the most common virtual thread mistake. Avoid `synchronized` blocks in virtual thread code. Use `ReentrantLock`, `StampedLock`, or lock-free data structures instead. Most Java libraries (JDBC, HTTP clients) are already virtual-thread-friendly.

### Performance Comparison
- **Platform threads**: ~1MB stack per thread; ~10K threads per JVM max.
- **Virtual threads**: ~KB stack per thread (grows on demand); millions of threads per JVM.
- **Throughput**: Virtual threads can 10-100x throughput for I/O-bound workloads.
- **Staff insight**: Virtual threads are not faster for CPU-bound work. They're better for I/O-bound work where threads spend most time blocked. For CPU-bound work, use platform threads or parallel streams.

### Migration Strategy
- **Start simple**: Replace `Executors.newFixedThreadPool()` with `Executors.newVirtualThreadPerTaskExecutor()`.
- **Remove reactive**: Convert reactive pipelines to synchronous code with virtual threads.
- **Fix pinning**: Replace `synchronized` blocks with lock-free alternatives.
- **Staff insight**: Virtual threads make reactive programming unnecessary for most use cases. The simplicity of synchronous code outweighs the performance benefits of reactive. Migrate incrementally: start with new services, then refactor existing ones.
