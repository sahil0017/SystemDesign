# Java Streams

## Overview

Stream API provides functional approach to processing collections. For staff engineers, streams are about **declarative data processing**, **composability**, and **knowing when NOT to use them** (performance-critical paths, complex stateful operations).

## Key Concepts

- **Intermediate vs terminal operations**: Intermediate (filter, map) are lazy; terminal (collect, forEach) trigger execution
- **Lazy evaluation**: Pipeline is built but not executed until terminal operation; enables optimization
- **Parallel streams**: ForkJoinPool.commonPool(); automatic parallelization; not always faster
- **Stream pipeline**: Source → intermediate operations → terminal operation; single-pass processing
- **Staff insight**: Streams are **not collections** — they don't store data; they process data. A stream can only be consumed once.

## Common Operations

### Intermediate (Lazy)
- **filter**: Predicate-based filtering; O(n)
- **map**: One-to-one transformation; O(n)
- **flatMap**: One-to-many transformation; flatten nested collections; O(n*m)
- **sorted**: Natural or custom comparator; O(n log n); materializes stream
- **distinct**: Deduplication using equals/hashCode; O(n); requires state
- **limit**: Short-circuiting; stops after N elements; enables early termination
- **skip**: Skip first N elements; O(n)
- **Staff insight**: **sorted() and distinct() are stateful** — they require seeing all elements. Place them at the end of the pipeline for optimization.

### Terminal (Eager)
- **forEach**: Unordered iteration; no guarantees on order
- **forEachOrdered**: Ordered iteration; loses parallelism benefit
- **collect**: Mutable reduction; most common terminal operation
- **reduce**: Immutable reduction; associative operation for parallel execution
- **count**: Count elements; O(n)
- **min/max**: Find min/max element; O(n)
- **anyMatch/allMatch/noneMatch**: Short-circuiting match; O(n) worst case
- **findFirst/findAny**: Find single element; findAny is faster for parallel streams
- **Staff insight**: Use **findAny** over **findFirst** for parallel streams — less ordering constraint enables better parallelism.

## Collectors

- **toList/toSet/toMap**: Basic collection; toMap needs merge function for duplicate keys
- **groupingBy**: Group elements by classifier; like SQL GROUP BY
- **partitioningBy**: Binary grouping (true/false); like SQL CASE WHEN
- **joining**: String concatenation; delimiter, prefix, suffix support
- **summarizing statistics**: count, sum, min, max, average in one pass
- **downstream collectors**: groupingBy + mapping, groupingBy + counting, etc.
- **Staff insight**: Use **groupingBy + counting** for frequency maps; **partitioningBy** for boolean splits.

## Best Practices

1. **Use streams for readability**: When the pipeline is clear and concise
2. **Avoid stateful operations**: sorted(), distinct(), limit() materialize the stream
3. **Prefer sequential for small datasets**: Parallel overhead > benefit for <10K elements
4. **Be careful with parallel streams**: Shared mutable state causes bugs; use findAny not findFirst
5. **Use map over flatMap when possible**: flatMap has higher overhead
6. **Avoid side effects in streams**: forEach with side effects is hard to reason about
7. **Profile stream performance**: Use JFR to measure actual throughput
8. **Prefer traditional loops for complex logic**: Streams add overhead; don't force them
- **Staff insight**: Streams are **not always faster**. For simple loops, traditional for-each is often faster due to less overhead.

## Problems (6)

| Problem | Key Concepts |
|---------|-------------|
| [Custom Collector Design](problems/custom-collector/) | Supplier, accumulator, combiner, charset flags |
| [Stream Pipeline Optimization](problems/stream-pipeline-optimization/) | Lazy evaluation, short-circuiting, stateful operations |
| [Parallel Stream Tuning](problems/parallel-stream-tuning/) | ForkJoinPool, work stealing, task granularity |
| [Stream vs Loop Benchmark](problems/stream-vs-loop/) | JMH comparison, primitive streams, dataset size impact |
| [Data Aggregation Pipeline](problems/data-aggregation/) | groupingBy, downstream collectors, summarizing statistics |
| [Reactive Stream Design](problems/reactive-stream/) | Backpressure, Publisher/Subscriber, virtual threads |

## Staff-Level Streams Checklist

1. **Use streams for declarative processing**: When the pipeline is clear and concise
2. **Avoid parallel streams unless necessary**: ForkJoinPool contention; measure first
3. **Use findAny for parallel streams**: Less ordering constraint; better parallelism
4. **Place stateful operations last**: sorted(), distinct() at end for optimization
5. **Avoid side effects in streams**: forEach with side effects is hard to reason about
6. **Use groupingBy for aggregations**: Like SQL GROUP BY; downstream collectors for complex aggregations
7. **Profile before optimizing**: Use JFR to measure actual throughput
8. **Prefer traditional loops for complex logic**: Streams add overhead; don't force them
