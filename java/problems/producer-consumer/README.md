# Producer-Consumer

## Problem Statement

Design a thread-safe producer-consumer system where multiple producer threads add items to a shared buffer and multiple consumer threads remove and process items.

**Reference**: AlgoMaster

## Requirements
- **Bounded buffer**: Fixed-size shared buffer between producers and consumers.
- **Blocking**: Producers block when buffer is full; consumers block when buffer is empty.
- **Thread safety**: Safe for multiple producers and consumers.

## Key Design Decisions
- **BlockingQueue**: `ArrayBlockingQueue` or `LinkedBlockingQueue` for the shared buffer.
- **wait/notify**: Custom implementation using `synchronized` with `wait()` and `notifyAll()`.
- **Semaphore**: Two semaphores (empty slots, filled slots) for coordination.

## Staff-Level Design Considerations
- **Staff insight**: Prefer `BlockingQueue` over manual `wait/notify`. It's battle-tested and handles edge cases (spurious wakeups, lost signals). If implementing from scratch, always use `while` loops (not `if`) around `wait()` to handle spurious wakeups.
