# ConcurrentHashMap Internals

## Problem Statement

Design and implement a thread-safe concurrent HashMap that allows high-throughput concurrent reads and writes using fine-grained locking, CAS operations, and lock striping.

**Reference**: [AlgoMaster](https://algomaster.io/), [Java Concurrency in Practice](https://www.oreilly.com/library/view/java-concurrency-in-practice/9780595279092/)

## Requirements

### Functional Requirements
- **Concurrent put/get**: Multiple threads can read/write simultaneously without blocking each other.
- **No null keys/values**: Unlike HashMap, reject null keys and values.
- **Atomic operations**: `putIfAbsent`, `remove(key, value)`, `replace(key, oldValue, newValue)`.
- **Compute operations**: `computeIfAbsent`, `computeIfPresent`, `merge` — atomic compute-and-update.
- **Iteration**: Weakly consistent iterators; no `ConcurrentModificationException`.
- **Size estimation**: `size()` returns approximate count during concurrent modifications.

### Non-Functional Requirements
- **High throughput**: Minimal lock contention under concurrent access.
- **Scalability**: Performance scales with number of cores.
- **Memory consistency**: All actions before lock release happen-before actions after lock acquisition.

## Key Design Decisions
- **Java 7 approach**: Segment-based locking (lock striping); 16 segments by default.
- **Java 8+ approach**: Node array + synchronized on bucket head + CAS for initial insert.
- **Treeification**: Like HashMap, convert buckets to red-black trees when collision count > 8.
- **CAS for empty bucket**: Lock-free insert when bucket is empty; fall back to synchronized.

## Staff-Level Design Considerations

### Java 7 vs Java 8 Design
- **Java 7 (Segmented)**: 16 `Segment` objects, each a mini-HashMap. Lock granularity = segment count.
  - **Pros**: Predictable lock granularity; good for high contention.
  - **Cons**: Fixed segment count; can't scale beyond segment count.
- **Java 8 (Bucket-level)**: Synchronize only the bucket head node where the key hashes.
  - **Pros**: Lock granularity = number of buckets; scales with map size.
  - **Cons**: Hot buckets can still cause contention.
- **Staff insight**: Java 8's approach is superior for most workloads because lock granularity adapts to map size. Only under extreme hash collision does it degrade.

### CAS + Synchronized Strategy
- **Step 1**: Check if bucket is empty. If yes, use CAS to insert.
- **Step 2**: If bucket is not empty, synchronize on bucket head and traverse list/tree.
- **Step 3**: For resize, use forwarding node to coordinate concurrent migration.
- **Staff insight**: The CAS-first approach means reads are almost always lock-free. Writes only block other writers to the same bucket, not the entire map.

### Weakly Consistent Iterators
- **No ConcurrentModificationException**: Iterators see a snapshot of the map's state at iteration start.
- **Structural changes**: New/removed entries may or may not appear during iteration.
- **Staff insight**: This is a key difference from HashMap. ConcurrentHashMap iterators never throw, making them safe for concurrent modification scenarios.

### Common Pitfalls
- **compound actions**: `if (!map.containsKey(k)) map.put(k, v)` is NOT atomic. Use `putIfAbsent()` instead.
- **Size accuracy**: `size()` is approximate during concurrent modifications. Use `mappingCount()` for long value.
- **Stream operations**: `forEach` and `search` methods provide better parallelism than streams.
- **Staff insight**: Never use `containsKey` + `put` as a check-then-act pattern. Always use atomic methods like `putIfAbsent`, `computeIfAbsent`, or `merge`.
