# CopyOnWriteArrayList

## Problem Statement

Design and implement a thread-safe list that uses copy-on-write semantics, where all mutations create a new copy of the underlying array, making it ideal for read-heavy concurrent scenarios.

**Reference**: [AlgoMaster](https://algomaster.io/), [Java Concurrency in Practice](https://www.oreilly.com/library/view/java-concurrency-in-practice/9780595279092/)

## Requirements

### Functional Requirements
- **Thread-safe get**: Lock-free reads; no synchronization overhead.
- **Copy on write**: Every mutation (add, set, remove) creates a new array copy.
- **Iterator**: Snapshot-based iterator; no `ConcurrentModificationException`.
- **List operations**: Support add, set, remove, get, size, contains.

### Non-Functional Requirements
- **Read performance**: O(1) lock-free reads with no contention.
- **Write performance**: O(n) copy overhead on every mutation.
- **Memory**: Each write allocates a new array; GC pressure under high write rate.

## Key Design Decisions
- **Array copy**: On every mutation, clone the entire array and apply the change.
- **Lock for writes**: `ReentrantLock` ensures only one writer at a time.
- **Lock-free reads**: Get operations read directly from the array without locking.
- **Snapshot iterator**: Iterator holds a reference to the array at creation time.

## Staff-Level Design Considerations

### When to Use
- **Read-heavy workloads**: Reads vastly outnumber writes (100:1 or more).
- **Listener lists**: Event listener registration where iteration is frequent and mutation is rare.
- **Configuration lists**: Lists that are read by many threads but updated infrequently.
- **Staff insight**: CopyOnWriteArrayList is perfect for observer patterns where the listener list is iterated frequently but modified rarely.

### Performance Trade-offs
- **Read cost**: O(1) lock-free; no cache invalidation; best possible read performance.
- **Write cost**: O(n) array copy + O(n) element copy; expensive for large lists.
- **Memory cost**: Each write creates a new array; old arrays become garbage.
- **Staff insight**: For lists with >1000 elements and frequent writes, CopyOnWriteArrayList will cause excessive GC pressure. Use `synchronizedList` or `ConcurrentHashMap` with atomic reference instead.

### Alternatives
- **synchronizedList**: Cheaper writes but reads are synchronized; lower read throughput.
- **ReadWriteLock + ArrayList**: Multiple concurrent readers; exclusive writer. Better for medium write rates.
- **Immutable list**: Create new list on each change; similar to copy-on-write but more explicit.
- **Staff insight**: If you need true immutability, consider using an immutable list library (e.g., Eclipse Collections ImmutableList). CopyOnWriteArrayList is mutable but provides snapshot semantics.

### Common Pitfalls
- **High write rate**: Every write copies the entire array; O(n) per mutation.
- **Memory leak**: Old arrays are not immediately collected; high write rate causes GC pressure.
- **Empty check**: `!list.isEmpty()` followed by `list.get(0)` is NOT atomic; another thread may clear the list.
- **Staff insight**: Never use CopyOnWriteArrayList for write-heavy scenarios. It's designed specifically for the case where iteration dominates mutation. If writes are frequent, use a different concurrent collection.
