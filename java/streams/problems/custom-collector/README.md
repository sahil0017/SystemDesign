# Custom Collector Design

## Problem Statement

Design a custom Collector for the Java Stream API that performs custom reduction logic, such as building a trie, computing weighted averages, or implementing a custom grouping strategy.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Collector interface**: Implement `Collector<T, A, R>` with supplier, accumulator, combiner, and finisher.
- **Supplier**: Create a new result container.
- **Accumulator**: Add an element to the result container.
- **Combiner**: Merge two result containers (for parallel streams).
- **Finisher**: Transform the result container to the final result.

### Non-Functional Requirements
- **Thread safety**: Accumulator and combiner must be thread-safe for parallel streams.
- **Performance**: Minimal overhead compared to built-in collectors.
- **Correctness**: Associative combiner for correct parallel reduction.

## Key Design Decisions
- **Collector.of()**: Factory method to create custom collectors.
- **Mutable reduction**: Accumulator mutates the result container; no intermediate allocations.
- **CHARSET flags**: UNORDERED, CONCURRENT, IDENTITY_FINISH for optimization hints.
- **Combiner**: Must be associative for correct parallel stream execution.

## Staff-Level Design Considerations

### Collector Implementation
```java
Collector<String, Trie, Trie> trieCollector = Collector.of(
    Trie::new,                          // Supplier
    (trie, word) -> trie.insert(word),  // Accumulator
    (trie1, trie2) -> { trie1.merge(trie2); return trie1; },  // Combiner
    Function.identity()                 // Finisher
);
```
- **Staff insight**: The combiner is the most critical part for parallel streams. It must be associative: `combine(a, combine(b, c)) == combine(combine(a, b), c)`. If the combiner isn't associative, parallel stream results will be incorrect.

### Charset Flags
- **UNORDERED**: The result doesn't depend on encounter order. Enables parallel optimization.
- **CONCURRENT**: The accumulator can be called from multiple threads concurrently. Required for true parallel reduction.
- **IDENTITY_FINISH**: The finisher is the identity function; skips the finish step.
- **Staff insight**: Setting CONCURRENT tells the stream framework that the accumulator is thread-safe. This allows multiple threads to accumulate into the same container without synchronization, dramatically improving parallel performance.

### Common Custom Collectors
- **Joining with limit**: Like `Collectors.joining()` but with a maximum length.
- **Weighted average**: Compute weighted average in a single pass.
- **Top-K**: Collect the K largest/smallest elements.
- **Deduplication**: Custom deduplication logic beyond `distinct()`.
- **Staff insight**: For top-K collection, use a PriorityQueue as the accumulator. The combiner merges two priority queues by offering all elements from one to the other. This is more efficient than sorting the entire stream.

### Common Pitfalls
- **Non-associative combiner**: Parallel streams produce incorrect results.
- **Thread-unsafe accumulator**: Concurrent modification exceptions in parallel streams.
- **Missing CONCURRENT flag**: Framework serializes accumulation even when accumulator is thread-safe.
- **Staff insight**: Always test custom collectors with both sequential and parallel streams. A collector that works correctly sequentially may fail in parallel due to combiner or thread safety issues.
