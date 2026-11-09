# CompletableFuture Advanced Patterns

## Problem Statement

Design and implement advanced asynchronous composition patterns using `CompletableFuture` including error handling, timeout, retry, fallback, and parallel aggregation for building resilient async pipelines.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Async composition**: Chain multiple async operations using `thenApply`, `thenCompose`, `thenAccept`.
- **Parallel execution**: Run multiple independent tasks in parallel using `allOf`, `anyOf`.
- **Error handling**: Graceful error recovery with `exceptionally`, `handle`, `whenComplete`.
- **Timeout**: Cancel long-running tasks with `orTimeout` (Java 9+) or custom timeout.
- **Retry with backoff**: Retry failed operations with exponential backoff.
- **Fallback**: Provide fallback values when primary operation fails.
- **Custom executor**: Run async tasks on a dedicated thread pool.

### Non-Functional Requirements
- **Non-blocking**: No thread blocking; use async callbacks.
- **Resilience**: Handle failures gracefully without propagating exceptions.
- **Performance**: Minimal overhead on async composition.
- **Thread safety**: All operations are thread-safe.

## Key Design Decisions
- **CompletableFuture chaining**: Use `thenCompose` for nested futures (flatMap equivalent), `thenApply` for simple transformation.
- **Exception handling**: `handle()` for unified success/failure processing; `exceptionally` for fallback.
- **Custom executor**: Avoid `ForkJoinPool.commonPool()`; use dedicated `ExecutorService` for production.
- **Timeout pattern**: Use `CompletableFuture.runAsync()` with `Future.get(timeout)` or Java 9+ `orTimeout()`.

## Staff-Level Design Considerations

### Composition Patterns
- **Sequential chain**: `future.thenApply(f1).thenApply(f2).thenApply(f3)` — each step depends on the previous.
- **Parallel fan-out**: `allOf(f1, f2, f3).thenApply(v -> combine(results))` — independent tasks run in parallel.
- **First winner**: `anyOf(f1, f2, f3)` — useful for multi-region reads; return first response.
- **Staff insight**: Use `thenCompose` (not `thenApply`) when the intermediate step returns a CompletableFuture. Using `thenApply` on a future wraps it in another future, creating `CompletableFuture<CompletableFuture<T>>`.

### Retry Pattern
```java
CompletableFuture<T> withRetry(Supplier<CompletableFuture<T>> supplier, int maxRetries) {
    return supplier.get().exceptionally(ex -> {
        if (retries < maxRetries) return withRetry(supplier, maxRetries).join();
        throw new RuntimeException(ex);
    });
}
```
- **Staff insight**: Add exponential backoff with jitter between retries to avoid thundering herd. Use `Thread.sleep()` in a separate thread or `delayedExecutor` for backoff.

### Timeout Pattern
- **Java 9+**: `future.orTimeout(5, TimeUnit.SECONDS)` — throws `TimeoutException`.
- **Java 8**: Wrap with `Future.get(timeout)` or use `CompletableFuture.runAsync(() -> {}, delayedExecutor)`.
- **Staff insight**: Always set timeouts on external calls (HTTP, DB, RPC). Without timeouts, a single slow dependency can exhaust your thread pool.

### Common Pitfalls
- **Blocking on async**: Calling `join()` or `get()` defeats the purpose of async; avoid in hot paths.
- **Exception swallowing**: Unhandled exceptions in `thenApply` complete the future exceptionally but may be silently ignored.
- **Thread pool exhaustion**: Using `commonPool()` for IO-bound tasks can starve other tasks.
- **Staff insight**: Always use a custom executor for IO-bound async tasks. Size it based on `N * (1 + W/C)` where N = cores, W = wait time, C = compute time.
