# Blocking Queue

## Problem Statement

Design a thread-safe blocking queue that supports put (blocks when full) and take (blocks when empty) operations.

**Reference**: AlgoMaster

## Requirements
- **Bounded capacity**: Fixed-size internal array.
- **put()**: Blocks when queue is full until space is available.
- **take()**: Blocks when queue is empty until an item is available.
- **Interruptible**: Support interruption while waiting.

## Key Design Decisions
- **Array-based**: Circular array with head and tail indices.
- **Condition variables**: Two conditions (notFull, notEmpty) for precise signaling.

## Staff-Level Design Considerations
- **Staff insight**: Use `ReentrantLock` with `newCondition()` for notFull and notEmpty. `notifyAll()` on `synchronized` wakes all threads; condition variables wake only the relevant ones. This is 10x more efficient under contention.
