# Structured Concurrency

## Problem Statement

Implement structured concurrency in Java (Java 21+) where related concurrent tasks are managed as a single unit of execution. All child tasks must complete before the parent scope exits, ensuring proper error handling, cancellation, and resource cleanup.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Task scope**: Group related tasks in a structured scope.
- **Fork/join**: Fork subtasks and join to wait for completion.
- **Error handling**: If any subtask fails, handle it at the scope level.
- **Cancellation**: Cancel all subtasks if one fails or timeout occurs.
- **Resource cleanup**: Ensure all resources are released when scope exits.
- **Stack representation**: Show all concurrent tasks in stack traces.

### Non-Functional Requirements
- **No orphaned tasks**: All tasks complete before scope exits.
- **Proper cancellation**: Failed tasks don't leave running siblings.
- **Clean stack traces**: Debug concurrent code with meaningful stack traces.

## Key Design Decisions
- **try-with-resources**: Scope implements AutoCloseable for guaranteed cleanup.
- **ShutdownOnFailure**: Cancel siblings when any task fails.
- **ShutdownOnSuccess**: Cancel siblings when any task succeeds (for racing tasks).
- **Virtual threads**: Structured concurrency works best with virtual threads.

## Implementation

```java
// Fork multiple tasks, wait for all, handle errors
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    // Fork subtasks
    Subtask<User> user = scope.fork(() -> fetchUser(userId));
    Subtask<Order> order = scope.fork(() -> fetchOrder(orderId));
    Subtask<List<Product>> products = scope.fork(() -> fetchProducts());

    // Wait for all to complete
    scope.join();

    // Throw if any failed
    scope.throwIfFailed();

    // Get results (all succeeded)
    User u = user.get();
    Order o = order.get();
    List<Product> p = products.get();

    process(u, o, p);
} // All tasks guaranteed completed here

// Race: first to win cancels others
try (var scope = new StructuredTaskScope.ShutdownOnSuccess()) {
    Subtask<String> primary = scope.fork(() -> callPrimaryService());
    Subtask<String> fallback = scope.fork(() -> callFallbackService());
    scope.join();
    String result = scope.select().get(); // Winner's result
}
```

## Staff-Level Design Considerations

### Structured Concurrency vs CompletableFuture
- **CompletableFuture**: Ad-hoc composition; easy to leak tasks; hard to cancel all.
- **Structured concurrency**: Explicit scope; guaranteed cleanup; clear hierarchy.
- **Staff insight**: **Migrate to structured concurrency** for new code. CompletableFuture chains are hard to reason about: who cancels what on error? Structured concurrency makes the lifecycle explicit: all tasks in a scope complete (success or failure) before the scope exits. This eliminates orphaned tasks and resource leaks.

### Error Handling Strategies
- **ShutdownOnFailure**: Cancel siblings on first failure — for all-or-nothing operations.
- **ShutdownOnSuccess**: Cancel siblings on first success — for racing fallbacks.
- **Custom**: Handle each task's result individually — for partial success scenarios.
- **Staff insight**: Use **ShutdownOnFailure** for API aggregation (fetch user + order + products — if any fails, cancel the rest). Use **ShutdownOnSuccess** for circuit breaker fallbacks (try primary, try fallback — use whichever responds first).

### Cancellation Propagation
- **Cooperative cancellation**: Tasks check `Thread.interrupted()` and throw.
- **HTTP cancellation**: `HttpClient` supports cancellation via interrupt.
- **DB cancellation**: JDBC doesn't support cancellation well — use timeouts.
- **Staff insight**: Make all tasks **cancellation-aware**. Check `Thread.currentThread().isInterrupted()` in loops. Use `HttpClient` which supports interrupt-based cancellation. For JDBC, set query timeouts — if a task is cancelled, the DB connection will timeout and release. Without cancellation awareness, structured concurrency can't clean up properly.

### Debugging Benefits
- **Stack traces**: All forked tasks appear in the parent's stack trace.
- **Thread dumps**: Show task hierarchy, not just flat thread list.
- **Staff insight**: Structured concurrency makes **thread dumps debuggable**. Instead of seeing 100 unrelated threads, you see a tree: "Scope: fetchDashboard → fork: fetchUser, fork: fetchOrders, fork: fetchProducts." This dramatically reduces incident response time when debugging concurrent code in production.
