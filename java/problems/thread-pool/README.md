# Thread Pool Design

## Problem Statement

Design a custom thread pool executor like Java's `ThreadPoolExecutor` that manages a pool of worker threads, queues tasks, and handles rejection policies.

**Reference**: AlgoMaster

## Requirements

### Functional Requirements
- **Core pool size**: Minimum number of threads kept alive.
- **Maximum pool size**: Maximum threads allowed under load.
- **Task queue**: Bounded/unbounded queue for pending tasks.
- **Rejection policy**: Reject tasks when pool and queue are full (Abort, CallerRuns, Discard, DiscardOldest).
- **Thread factory**: Custom thread naming and configuration.
- **Shutdown**: Graceful shutdown with task completion.

### Non-Functional Requirements
- **Thread safety**: All operations are thread-safe.
- **Performance**: Minimal overhead on task submission and execution.

## Key Design Decisions
- **Worker threads**: Each worker loops, taking tasks from the queue and executing them.
- **Queue**: `BlockingQueue<Runnable>` for thread-safe task handoff.
- **Dynamic sizing**: Add threads up to maxPoolSize when queue is full.

## Staff-Level Design Considerations

### Queue Selection
- **ArrayBlockingQueue**: Bounded; triggers new thread creation when full. Good for controlling memory.
- **LinkedBlockingQueue**: Unbounded by default; never triggers new threads. Risk of OOM.
- **SynchronousQueue**: Direct handoff; always creates new thread. Good for short-lived tasks.
- **Staff insight**: The queue choice determines thread pool behavior. For bounded resources, use ArrayBlockingQueue. For unbounded workloads, use a bounded queue with a rejection policy.

### Rejection Policy
- **CallerRuns**: The calling thread executes the task. Provides natural backpressure.
- **Staff insight**: CallerRuns is the best default. It slows down the producer when the pool is overwhelmed, preventing OOM. Abort is too aggressive; Discard loses work silently.
