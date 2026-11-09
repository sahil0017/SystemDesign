# CompletableFuture Deep Dive

## Overview

CompletableFuture (Java 8+) enables asynchronous programming with composability. It allows chaining, combining, and transforming async results without callback hell — the foundation of non-blocking Java applications.

## Basic Usage

```java
// Create async task
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    return fetchDataFromAPI();
});

// Transform result
CompletableFuture<Integer> length = future.thenApply(String::length);

// Handle exception
CompletableFuture<String> safe = future.exceptionally(ex -> "default");

// Block and get result
String result = future.get();
```

## Chaining Operations

### Sequential Chaining
```java
CompletableFuture<User> user = CompletableFuture
    .supplyAsync(() -> findById(id))
    .thenApply(user -> enrichUser(user))
    .thenApply(user -> applyDiscount(user))
    .exceptionally(ex -> getDefaultUser());
```

### Async Continuation
```java
// thenApply: runs on same thread as previous stage
future.thenApply(this::process);

// thenApplyAsync: runs on ForkJoinPool (different thread)
future.thenApplyAsync(this::process);

// thenApplyAsync with custom executor
future.thenApplyAsync(this::process, ioExecutor);
```

## Combining Futures

```java
// Combine two futures
CompletableFuture<Void> combined = CompletableFuture.allOf(future1, future2);

// Zip two futures
CompletableFuture<Result> zipped = future1.thenCombine(future2, (r1, r2) -> {
    return new Result(r1, r2);
});

// Race two futures (whichever completes first)
CompletableFuture<String> fastest = CompletableFuture.anyOf(future1, future2)
    .thenApply(obj -> (String) obj);
```

## Error Handling

```java
// Handle exception, continue with default
future.orElseGet(() -> defaultValue);

// Handle exception, return alternative future
future.orElseAsync(() -> alternativeFuture());

// Complete with exception
future.completeExceptionally(new RuntimeException("error"));

// Handle all exceptions at the end
future.whenComplete((result, ex) -> {
    if (ex != null) log.error("Failed", ex);
});
```

## Staff-Level Insights

### Executor Selection
- **Never use default ForkJoinPool** for I/O operations — it's CPU-optimized
- Use **custom executors** for I/O-bound tasks with appropriate thread count
- **Staff insight**: `CompletableFuture.supplyAsync()` uses ForkJoinPool.commonPool() by default. For I/O, always provide a custom executor: `supplyAsync(task, ioExecutor)`.

### Timeout Handling
```java
// Race with timeout
CompletableFuture<String> withTimeout = CompletableFuture.anyOf(
    future,
    CompletableFuture.completedFuture(null).delayed(5, TimeUnit.SECONDS)
);
```
- **Staff insight**: Always set timeouts on async operations. Without timeouts, a slow dependency can hold threads indefinitely, causing resource exhaustion.

### Cancellation
- `future.cancel(true)` interrupts the running thread
- Check `Thread.currentThread().isInterrupted()` in long-running tasks
- **Staff insight**: Cancellation is cooperative. If your async task doesn't check for interruption, `cancel()` won't stop it. Design tasks to be cancellable by checking interruption status periodically.

### Avoiding Common Pitfalls
- **Fire-and-forget**: Unhandled exceptions in CompletableFuture are swallowed — always attach `exceptionally()` or `whenComplete()`
- **Blocking in async**: Don't call `.get()` inside async tasks — defeats the purpose
- **Staff insight**: Use `handle()` instead of `thenApply()` + `exceptionally()` — it handles both success and failure in one step, reducing boilerplate.
