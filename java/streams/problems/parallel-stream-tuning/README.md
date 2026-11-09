# Parallel Stream Tuning

## Problem Statement

Design a strategy for tuning Java parallel streams to achieve optimal performance, including ForkJoinPool configuration, task granularity, and when parallel streams actually help.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **ForkJoinPool configuration**: Customize common pool parallelism and create custom pools.
- **Task granularity**: Determine optimal chunk size for parallel processing.
- **Work stealing**: Understand how ForkJoinPool distributes work across threads.
- **Performance measurement**: Benchmark parallel vs sequential stream performance.

### Non-Functional Requirements
- **Scalability**: Performance improves with CPU cores up to a point.
- **No contention**: Avoid shared mutable state in parallel operations.
- **Predictability**: Consistent performance across different dataset sizes.

## Key Design Decisions
- **Common pool**: `ForkJoinPool.commonPool()` shared by all parallel streams; default parallelism = CPU cores - 1.
- **Custom pool**: Create dedicated ForkJoinPool for specific workloads to avoid contention.
- **Spliterator**: Custom spliterator for efficient data splitting.
- **findAny vs findFirst**: Use findAny for parallel streams to avoid ordering overhead.

## Staff-Level Design Considerations

### When Parallel Streams Help
- **Large datasets**: >100K elements; overhead of task splitting is amortized.
- **CPU-bound operations**: Heavy computation per element benefits from parallelism.
- **Independent elements**: No dependency between elements; no shared mutable state.
- **Staff insight**: Parallel streams rarely help for small datasets (<10K elements) or IO-bound operations. The task splitting and thread coordination overhead exceeds the benefit. Always benchmark before using parallel streams.

### ForkJoinPool Configuration
```java
// Custom pool with specific parallelism
ForkJoinPool customPool = new ForkJoinPool(4);
list.parallelStream().forEach(...)  // Uses common pool
list.stream().parallel().forEach(...)  // Uses common pool
customPool.submit(() -> list.parallelStream().forEach(...))  // Uses custom pool
```
- **Staff insight**: Never use the common ForkJoinPool for IO-bound tasks. It's shared by all parallel operations in the JVM. If one task blocks on IO, it starves all other parallel operations. Create a custom ForkJoinPool for IO-bound work.

### Common Pool Pitfalls
- **Shared resource**: All parallel streams in the JVM share the common pool. A slow stream blocks all others.
- **Blocking tasks**: If a parallel stream task blocks (IO, sleep), it wastes a pool thread.
- **Parallelism = N-1**: Common pool reserves one core for other tasks (e.g., timer, interrupt).
- **Staff insight**: The common pool's parallelism is N-1 (where N = CPU cores). This reserves one core for non-ForkJoin tasks. If your application only uses parallel streams, you can increase parallelism with `System.setProperty("java.util.concurrent.ForkJoinPool.common.parallelism", String.valueOf(Runtime.getRuntime().availableProcessors()))`.

### Performance Tuning
- **Dataset size**: Use parallel streams only for >100K elements with CPU-bound operations.
- **Custom spliterator**: For custom data structures, implement a spliterator that splits efficiently.
- **Avoid ordering**: `forEach()` is faster than `forEachOrdered()` in parallel streams.
- **Use findAny**: `findAny()` is faster than `findFirst()` in parallel streams.
- **Staff insight**: The biggest performance win in parallel streams is avoiding ordering constraints. `forEachOrdered()` and `findFirst()` require coordination between threads to maintain order, which eliminates most of the parallelism benefit. Use `forEach()` and `findAny()` whenever order doesn't matter.
