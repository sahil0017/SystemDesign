# Thread Pool (Concurrency)

## Problem Statement

Design a custom thread pool that manages a fixed number of worker threads to execute submitted tasks concurrently. The thread pool should handle task queuing, worker lifecycle management, rejection policies, and graceful shutdown.

**Reference**: LLD Coding

## Requirements

### Functional Requirements
- **Submit task**: Add a Runnable/Callable task to the pool for execution.
- **Worker threads**: Fixed number of worker threads that pull tasks from a queue.
- **Task queue**: Bounded queue for pending tasks.
- **Rejection policy**: Handle tasks when queue is full (reject, caller-runs, abort, oldest-drop).
- **Shutdown**: Graceful shutdown that completes pending tasks before stopping.
- **Metrics**: Track active threads, completed tasks, queue size, and rejected tasks.

### Non-Functional Requirements
- **Thread safety**: Safe for concurrent task submission from multiple threads.
- **No thread leak**: Workers are properly managed and can be recycled.
- **Graceful degradation**: Handle overload without crashing.
- **Configurable**: Adjustable pool size, queue capacity, and rejection policy.

## Key Design Decisions
- **Work queue**: `BlockingQueue` for task storage; workers block when queue is empty.
- **Worker loop**: Each worker continuously polls the queue for tasks.
- **Strategy pattern**: Pluggable rejection policies.
- **Lifecycle management**: States: RUNNING → SHUTDOWN → STOP → TERMINATED.

## Class Diagram

```
┌──────────────────────┐     ┌──────────────────────┐
│    ThreadPool        │────►│    WorkerThread       │
├──────────────────────┤     ├──────────────────────┤
│ - workers: List      │     │ - thread: Thread     │
│ - taskQueue          │     │ - pool: ThreadPool   │
│ - corePoolSize       │     ├──────────────────────┤
│ - maxPoolSize        │     │ + run()              │
│ - rejectionPolicy    │     │ + interrupt()        │
│ - state              │     └──────────────────────┘
├──────────────────────┤
│ + submit(task)       │
│ + shutdown()         │
│ + getMetrics()       │
└──────────────────────┘
```

## Staff-Level Design Considerations

### Worker Thread Lifecycle
- **Daemon vs non-daemon**: Worker threads should be non-daemon to ensure task completion.
- **Staff insight**: Daemon threads are killed when the main thread exits, potentially losing tasks. Use non-daemon workers and implement proper shutdown hooks.

### Rejection Policies
- **CallerRuns**: Submitting thread executes the task — provides backpressure.
- **Abort**: Throw exception — fails fast.
- **DiscardOldest**: Remove oldest task and try again — prioritizes recent tasks.
- **Staff insight**: `CallerRunsPolicy` is the best default — it naturally provides backpressure by slowing down the producer. Don't silently discard tasks in production — always log rejected tasks.

### Queue Selection
- **SynchronousQueue**: Zero capacity; handoff directly to worker. Best for unbounded pools.
- **ArrayBlockingQueue**: Fixed capacity; predictable memory usage.
- **LinkedBlockingQueue**: Unbounded by default; risk of OOM.
- **Staff insight**: Never use an unbounded queue in production — it will OOM under load. Use `ArrayBlockingQueue` with a reasonable capacity and a rejection policy.

### Graceful Shutdown
- **Two-phase shutdown**: `shutdown()` stops accepting new tasks; `awaitTermination()` waits for pending tasks.
- **Staff insight**: Don't interrupt workers immediately — let them complete current tasks. Use `shutdown()` followed by `awaitTermination(timeout)`, then `shutdownNow()` if needed.
