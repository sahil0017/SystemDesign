# Stream Pipeline Optimization

## Problem Statement

Design and optimize Java Stream pipelines for maximum performance by understanding lazy evaluation, intermediate operation ordering, short-circuiting, and when to avoid streams entirely.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Lazy evaluation**: Understand when intermediate operations are executed.
- **Operation ordering**: Place expensive operations after cheap filters.
- **Short-circuiting**: Use limit, findFirst, anyMatch for early termination.
- **Stateful operations**: Understand sorted, distinct, and dedup overhead.
- **Terminal operations**: Choose the right terminal operation for the use case.

### Non-Functional Requirements
- **Performance**: Stream pipeline matches or exceeds traditional loop performance.
- **Readability**: Declarative code that's easy to understand and maintain.
- **Memory efficiency**: Minimal intermediate allocations.

## Key Design Decisions
- **Filter first**: Place filter operations early to reduce the number of elements processed.
- **Map before flatMap**: Use map when possible; flatMap has higher overhead.
- **Stateful last**: Place sorted() and distinct() at the end of the pipeline.
- **Terminal choice**: Use findAny() for parallel streams; forEachOrdered() when order matters.

## Staff-Level Design Considerations

### Pipeline Optimization Rules
- **Filter early**: `stream.filter(cheap).filter(expensive).map(transform)` — cheap filter reduces elements before expensive filter.
- **Avoid stateful operations**: `sorted()` and `distinct()` materialize the entire stream. Use only when necessary.
- **Short-circuit when possible**: `limit(n)` stops after n elements; `anyMatch()` stops on first match.
- **Staff insight**: The stream pipeline is evaluated element by element, not operation by operation. For each element, all intermediate operations are applied before moving to the next element. This means placing filter before map doesn't change when map is called — it's called for each element that passes the filter.

### When to Avoid Streams
- **Simple loops**: `for (Item i : list) sum += i.value()` is faster and clearer than a stream.
- **Complex state**: Streams with external mutable state are hard to reason about and bug-prone.
- **Performance-critical paths**: Streams add overhead (lambda creation, method handles).
- **Small datasets**: Parallel stream overhead exceeds benefit for <10K elements.
- **Staff insight**: Streams are a readability tool, not a performance tool. Use them when the pipeline is clear and concise. For complex logic or performance-critical paths, use traditional loops.

### Common Anti-Patterns
- **Side effects in forEach**: Modifying external state in forEach is hard to debug and breaks parallelism.
- **Collect then stream**: `list.stream().collect(...).stream()` — two passes when one would suffice.
- **Parallel stream on small data**: ForkJoinPool overhead exceeds benefit for small datasets.
- **Boxing in streams**: `IntStream` vs `Stream<Integer>` — use primitive streams to avoid boxing.
- **Staff insight**: Always use primitive streams (`IntStream`, `LongStream`, `DoubleStream`) when working with primitives. `Stream<Integer>` boxes every int to an Integer object, doubling memory usage and adding GC pressure.

### Performance Comparison
- **Sequential stream vs loop**: Loop is 10-30% faster due to less overhead.
- **Parallel stream vs sequential**: 2-4× faster for CPU-bound operations on large datasets (>100K elements).
- **Stream with stateful ops**: sorted() and distinct() can be 2-5× slower than equivalent loop code.
- **Staff insight**: Benchmark your stream pipelines with JMH. The performance difference between streams and loops depends on the operations, dataset size, and JVM version. Don't assume streams are slower — profile first.
