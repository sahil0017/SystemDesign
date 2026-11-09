# Concurrent HashMap (Concurrency)

## Problem Statement

Design a thread-safe hash map that supports concurrent reads and writes with high throughput. The implementation should handle put, get, remove, and iterate operations without global locking, using fine-grained segmentation or lock-free techniques.

**Reference**: AlgoMaster

## Requirements

### Functional Requirements
- **put(key, value)**: Insert or update a key-value pair.
- **get(key)**: Retrieve value for a key; return null if not found.
- **remove(key)**: Remove a key-value pair.
- **containsKey(key)**: Check if a key exists.
- **size()**: Return number of entries.
- **iterate()**: Safe iteration without ConcurrentModificationException.
- **resize()**: Dynamic resizing when load factor threshold is exceeded.

### Non-Functional Requirements
- **Thread safety**: Full thread safety for all operations.
- **High throughput**: Concurrent writes to different buckets should not block each other.
- **No global lock**: Avoid a single lock that serializes all operations.
- **Weakly consistent iteration**: Iterators reflect state at some point since creation.

## Key Design Decisions
- **Segment locking**: Divide map into segments; each segment has its own lock.
- **CAS operations**: Use Compare-And-Swap for lock-free bucket updates.
- **Striped counters**: Use multiple counters for size tracking to reduce contention.
- **Tree bins**: Convert linked list bins to balanced trees when bin size > 8 (like Java 8+ ConcurrentHashMap).

## Class Diagram

```
┌──────────────────────┐     ┌──────────────────────┐
│  ConcurrentHashMap   │────►│      Segment         │
├──────────────────────┤     ├──────────────────────┤
│ - segments           │     │ - lock: ReentrantLock│
│ - segmentMask        │     │ - table: Node[]      │
│ - counterCells       │     │ - count              │
├──────────────────────┤     └──────────────────────┘
│ + put(key, value)    │
│ + get(key)           │
│ + remove(key)        │
│ + size()             │
│ + resize()           │
└──────────────────────┘
```

## Staff-Level Design Considerations

### Segment Locking Strategy
- **Fine-grained locks**: Each segment locks independently; writes to different segments don't block.
- **Staff insight**: Java 8+ ConcurrentHashMap moved from segments to bucket-level locking. Each bucket head is locked individually, providing even finer granularity than segments.

### CAS for Lock-Free Updates
- **Compare-And-Swap**: Update bucket without locking if no contention.
- **Staff insight**: CAS is the foundation of lock-free data structures. Under low contention, CAS avoids lock acquisition overhead. Under high contention, fall back to locking to avoid infinite spinning.

### Size Counter Contention
- **Striped counters**: Multiple `LongAdder` cells; threads update different cells to avoid CAS contention.
- **Staff insight**: A single `AtomicInteger` for size becomes a bottleneck under high write throughput. `LongAdder` stripes counters across threads, reducing contention by ~10x under heavy writes.

### Tree Bins for Worst-Case Protection
- **Hash collision attack**: Malicious input can force all keys into one bin → O(n) lookup.
- **Staff insight**: Java 8+ converts bins to `TreeBin` (red-black tree) when bin size > 8. This guarantees O(log n) worst-case instead of O(n). This is a defense against hash collision DoS attacks.
