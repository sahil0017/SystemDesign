# Concurrent Bloom Filter (Concurrency)

## Problem Statement

Design a thread-safe Bloom filter that supports concurrent additions and lookups. The Bloom filter should provide probabilistic membership testing with configurable false positive rate, supporting high-throughput concurrent access without global locking.

**Reference**: AlgoMaster

## Requirements

### Functional Requirements
- **add(item)**: Add an item to the Bloom filter.
- **contains(item)**: Check if an item might be in the filter (may return false positives).
- **hash functions**: Multiple independent hash functions for bit array indexing.
- **Configurable size**: Set bit array size and number of hash functions based on expected items and false positive rate.
- **Statistics**: Track number of items added and estimated false positive rate.

### Non-Functional Requirements
- **Thread safety**: Concurrent adds and contains without data corruption.
- **High throughput**: No global lock; parallel hash computation.
- **Memory efficiency**: Fixed memory usage regardless of number of items.
- **No false negatives**: If contains() returns true, item may or may not be present. If false, item is definitely not present.

## Key Design Decisions
- **BitSet/atomic bit array**: Use `AtomicLongArray` for thread-safe bit operations.
- **Multiple hash functions**: Use double-hashing technique (two hash functions combined) for efficiency.
- **Lock-free reads**: Reading bits is inherently lock-free with atomic operations.
- **Striped writes**: Divide bit array into stripes; each stripe has its own lock for writes.

## Class Diagram

```
┌──────────────────────┐
│ BloomFilter          │
├──────────────────────┤
│ - bits: AtomicLongArray│
│ - numHashFunctions   │
│ - expectedItems      │
│ - falsePositiveRate  │
│ - seeds: int[]       │
├──────────────────────┤
│ + add(item)          │
│ + contains(item)     │
│ + hash(item, i)      │
│ + getFalsePositiveRate()│
└──────────────────────┘
```

## Staff-Level Design Considerations

### Thread-Safe Bit Operations
- **AtomicLongArray**: Each bit is accessed via CAS on the containing long word.
- **Staff insight**: `java.util.BitSet` is not thread-safe. Use `AtomicLongArray` where each long represents 64 bits. The `get()` operation is lock-free; `set()` uses CAS.

### Double Hashing Technique
- **Two hash functions**: h(i) = h1 + i*h2, where h1 and h2 are two independent hash functions.
- **Staff insight**: Instead of k independent hash functions (expensive), use two hash functions and combine them. This is the standard technique in production Bloom filters (Google's Swiss Table, Redis).

### False Positive Rate Calculation
- **Formula**: p ≈ (1 - e^(-kn/m))^k, where k = hash functions, n = items, m = bits.
- **Staff insight**: The optimal number of hash functions is k = (m/n) * ln(2). For a 1% false positive rate, you need ~10 bits per item. Don't use too many hash functions — they increase false positives after the optimal point.

### Production Alternatives
- **Cuckoo filter**: Supports deletion; similar false positive rate; better for dynamic workloads.
- **Staff insight**: Bloom filters don't support deletion. If you need deletion, use a Cuckoo filter. If you need exact counts, use a HyperLogLog or Count-Min Sketch.
