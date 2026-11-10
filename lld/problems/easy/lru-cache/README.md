# LRU Cache

## Problem Statement

Design and implement an LRU (Least Recently Used) cache that supports `get` and `put` operations in O(1) time complexity.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **get(key)**: Return the value if key exists, otherwise return -1. Mark the key as recently used.
- **put(key, value)**: Insert or update the key-value pair. If cache is at capacity, evict the LRU entry before inserting.
- **Capacity**: Fixed maximum size defined at construction time.
- **Access tracking**: Both read and write operations update the "recently used" order.

- Support get(key) operation: returns the value if the key exists, otherwise returns null or -1
- Support put(key, value) operation: inserts a new key-value pair or updates the value of an existing key
- If the cache exceeds its capacity, it should automatically evict the least recently used item.
- Both get and put operations should update the recency of the accessed or inserted item.
- Keys and values should be generic (e.g., <K, V>), provided the keys are hashable.

### Non-Functional Requirements
- **Time complexity**: O(1) for both get and put operations.
- **Thread safety**: Support concurrent reads; optional concurrent writes.
- **Memory efficiency**: No memory leaks; evicted entries are garbage collected.
- Time Complexity: Both get and put operations must run in O(1) time on average.
- Thread Safety: The implementation must be thread-safe for use in concurrent environments.
- Modularity: The design should follow object-oriented principles with clean separation of responsibilities.
- Memory Efficiency: The internal data structures should be optimized for speed and space within the defined constraints.


## Key Design Decisions
- **Data structure**: HashMap + Doubly Linked List for O(1) lookup and O(1) insertion/deletion.
- **HashMap**: Maps key → node in linked list for O(1) access.
- **Doubly Linked List**: Maintains usage order; head = most recent, tail = least recent.
- **Thread safety**: Use `ReentrantReadWriteLock` for concurrent reads with exclusive write access.

## Class Diagram

```
┌─────────────────────┐
│    LRUCache         |
├─────────────────────┤
│ - capacity: int     │
│ - cache: HashMap    │
│ - dll: DLL          │
├─────────────────────┤
│ + get(key): int     │
│ + put(key, val): void│
└─────────┬───────────┘
          │ uses
┌─────────┴───────────┐     ┌──────────────┐
│    DLL              │────►│    Node       │
├─────────────────────┤     ├──────────────┤
│ - head: DummyNode   │     │ - key: int    │
│ - tail: DummyNode   │     │ - value: int  │
│ - size: int         │     │ - prev: Node  │
├─────────────────────┤     │ - next: Node  │
│ + addToFront(node)  │     └──────────────┘
│ + removeNode(node)  │
│ + removeTail()      │
└─────────────────────┘
```

## Staff-Level Design Considerations

### O(1) Guarantee
- **HashMap + DLL** is the canonical approach. A TreeMap-based solution gives O(log n) — not acceptable.
- **Staff insight**: Dummy head/tail nodes eliminate boundary checks, reducing bugs by ~40%.

### Thread Safety
- **ReadWriteLock**: Multiple readers, single writer. Better throughput than `synchronized` for read-heavy workloads.
- **Staff insight**: For extreme concurrency, consider `ConcurrentHashMap` + segmented locks, but complexity increases significantly.

### Production Variants
- **Caffeine/Guava Cache**: Production-grade implementations with window-based LRU, async reload, and eviction listeners.
- **Staff insight**: Don't roll your own cache in production. Use Caffeine — it outperforms Guava and has advanced eviction policies.
