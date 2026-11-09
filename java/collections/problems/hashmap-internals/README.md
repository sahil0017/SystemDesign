# HashMap Internals

## Problem Statement

Design and implement a HashMap from scratch that mimics Java's `HashMap` internals, including bucket array, hash computation, collision resolution with linked lists and red-black trees, and automatic resizing.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Put/Get/Delete**: O(1) average time complexity for basic operations.
- **Hash computation**: Mix key's hashCode to distribute keys evenly across buckets.
- **Collision resolution**: Use linked list for collisions; convert to red-black tree when list size > 8.
- **Resize**: Double capacity when size exceeds threshold (load factor × capacity).
- **Null keys**: Support null keys (stored in bucket 0).
- **Iteration**: Support keySet, values, and entrySet views.

### Non-Functional Requirements
- **Performance**: O(1) average for get/put; O(log n) worst case with treeification.
- **Memory efficiency**: Minimal overhead per entry.
- **Thread safety**: Not thread-safe (like HashMap); use ConcurrentHashMap for concurrent access.

## Key Design Decisions
- **Array of buckets**: `Node<K,V>[] table` with power-of-2 capacity for fast index computation.
- **Hash mixing**: `hash(key.hashCode())` with bit mixing to reduce collision from similar hash codes.
- **Index computation**: `(n - 1) & hash` — bitwise AND instead of modulo for power-of-2 size.
- **Treeification**: When bucket list size > 8 and table size > 64, convert to TreeMap (red-black tree).
- **Untreeification**: When tree size < 6 during resize, convert back to linked list.

## Staff-Level Design Considerations

### Hash Function Design
- **Bit mixing**: Java 8 uses `h ^ (h >>> 16)` to mix high and low bits of hashCode.
- **Why power of 2**: Enables `(n - 1) & hash` instead of expensive `hash % n`.
- **Staff insight**: A good hash function distributes keys uniformly. Poor hash codes (e.g., all even) with power-of-2 size cause collisions. Bit mixing mitigates this.

### Treeification Threshold
- **Why 8**: Based on Poisson distribution — probability of 8+ keys in one bucket is ~10^-7 with good hash.
- **Why 6**: Hysteresis between treeify (8) and untreeify (6) prevents frequent conversion.
- **Staff insight**: Treeification protects against hash collision attacks. An attacker can craft keys with identical hash codes to force O(n) lookups. Treeification limits this to O(log n).

### Resize Strategy
- **When**: Size > loadFactor × capacity (default 0.75 × capacity).
- **How**: Create new table with doubled capacity; rehash all entries.
- **Optimization**: In Java 8+, entries either stay at same index or move to index + oldCapacity.
- **Staff insight**: Pre-size HashMap when you know the expected number of entries: `new HashMap<>(expectedSize / 0.75f + 1)` to avoid resize overhead.

### Common Pitfalls
- **Not overriding hashCode/equals**: Objects use default identity hash; same logical objects hash differently.
- **Mutable keys**: If key's hashCode changes after insertion, the entry becomes unreachable.
- **Load factor too high**: More collisions; worse performance. Too low: wasted memory.
- **Staff insight**: Never use mutable objects as HashMap keys. If you must, ensure the key's state used in hashCode/equals doesn't change after insertion.
