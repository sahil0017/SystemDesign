# Thread-Safe Blocking Queue (Concurrency)

## Problem Statement

Design a thread-safe blocking queue that supports concurrent producers and consumers. Producers block when the queue is full, and consumers block when the queue is empty. The implementation should use condition variables or semaphores for efficient waiting.

**Reference**: AlgoMaster

## Requirements

### Functional Requirements
- **put(item)**: Add an item; block if queue is full until space is available.
- **take()**: Remove and return an item; block if queue is empty until an item is available.
- **offer(item, timeout)**: Add an item with timeout; return false if timeout expires.
- **poll(timeout)**: Remove and return an item with timeout; return null if timeout expires.
- **peek()**: View the head without removing; non-blocking.
- **size()**: Return current number of items.
- **isEmpty() / isFull()**: Check queue state.

### Non-Functional Requirements
- **Thread safety**: Safe for multiple producers and consumers.
- **No busy-waiting**: Threads wait efficiently using condition variables.
- **Fairness**: Optional FIFO ordering for waiting threads.
- **Bounded capacity**: Fixed maximum size to prevent OOM.

## Key Design Decisions
- **Array-based**: Circular array for O(1) enqueue/dequeue.
- **Condition variables**: `notFull` and `notEmpty` conditions for blocking.
- **ReentrantLock**: Single lock for queue operations with condition variables.
- **Interruptible**: Support thread interruption during blocking operations.

## Class Diagram

```
┌──────────────────────┐
│ BlockingQueue         │
├──────────────────────┤
│ - array: T[]         │
│ - capacity           │
│ - count              │
│ - head, tail         │
│ - lock: ReentrantLock│
│ - notEmpty: Condition│
│ - notFull: Condition │
├──────────────────────┤
│ + put(item)          │
│ + take()             │
│ + offer(item, timeout)│
│ + poll(timeout)      │
│ + peek()             │
│ + size()             │
└──────────────────────┘
```

## Staff-Level Design Considerations

### Condition Variables vs Wait/Notify
- **Condition variables**: `ReentrantLock.newCondition()` provides precise signaling.
- **Staff insight**: `wait()/notify()` on `synchronized` blocks can wake the wrong thread (spurious wakeups + signal loss). Condition variables separate "not empty" from "not full" — producers wait on `notFull`, consumers wait on `notEmpty`.

### Spurious Wakeups
- **Loop check**: Always check the condition in a loop after waking.
- **Staff insight**: The JVM spec allows spurious wakeups. Never use `if (condition)` — always use `while (!condition)` before `await()`. This is a common interview trap.

### Interrupt Handling
- **InterruptedException**: Blocking operations should respond to thread interruption.
- **Staff insight**: When a thread is interrupted during `put()` or `take()`, restore the interrupt status with `Thread.currentThread().interrupt()` before rethrowing. This preserves the interrupt signal for callers.

### Array vs Linked Implementation
- **Array-based**: Better cache locality; fixed capacity; no object allocation on enqueue.
- **Staff insight**: `ArrayBlockingQueue` (array-based) outperforms `LinkedBlockingQueue` (node-based) in most scenarios due to cache locality and no node allocation. Use array-based unless you need unbounded capacity.
