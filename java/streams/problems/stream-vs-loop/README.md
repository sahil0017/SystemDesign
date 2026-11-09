# Stream vs Loop Benchmark

## Problem Statement

Design a comprehensive benchmark that compares Java Stream API performance against traditional for-loops across various operations (filter, map, reduce, grouping) to determine when streams are appropriate.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Filter benchmark**: Compare stream.filter() vs for-loop with if-condition.
- **Map benchmark**: Compare stream.map() vs for-loop with transformation.
- **Reduce benchmark**: Compare stream.reduce() vs for-loop with accumulator.
- **Grouping benchmark**: Compare stream.groupingBy() vs for-loop with HashMap.
- **Dataset sizes**: Test with 1K, 10K, 100K, and 1M elements.

### Non-Functional Requirements
- **Accuracy**: Use JMH for proper warm-up and statistical significance.
- **Reproducibility**: Same benchmark produces consistent results.
- **Comprehensive**: Cover common stream operations and patterns.

## Key Design Decisions
- **JMH framework**: Proper warm-up, forks, and statistical analysis.
- **@Param for sizes**: Test multiple dataset sizes in one benchmark.
- **Blackhole**: Consume results to prevent dead-code elimination.
- **Multiple modes**: Throughput and AverageTime for different perspectives.

## Staff-Level Design Considerations

### Expected Results
- **Small datasets (<10K)**: Loop is 20-50% faster; stream overhead dominates.
- **Medium datasets (10K-100K)**: Loop is 10-20% faster; streams approach loop performance.
- **Large datasets (>100K)**: Streams are within 5-10% of loop performance.
- **Complex operations**: Streams can be slower due to lambda allocation and method handle overhead.
- **Staff insight**: The performance gap between streams and loops has narrowed in recent JVM versions (Java 11+). The JIT compiler optimizes lambda calls aggressively. For most applications, the readability benefit of streams outweighs the small performance difference.

### Benchmark Design
```java
@Param({"1000", "10000", "100000", "1000000"})
private int size;

@Setup(Level.Iteration)
public void setup() {
    data = IntStream.range(0, size).boxed().collect(Collectors.toList());
}

@Benchmark
public int loopFilter(Blackhole bh) {
    int sum = 0;
    for (Integer i : data) {
        if (i % 2 == 0) sum += i;
    }
    bh.consume(sum);
    return sum;
}

@Benchmark
public int streamFilter(Blackhole bh) {
    int sum = data.stream()
        .filter(i -> i % 2 == 0)
        .mapToInt(Integer::intValue)
        .sum();
    bh.consume(sum);
    return sum;
}
```
- **Staff insight**: Use `@Setup(Level.Iteration)` to recreate the dataset before each iteration. This prevents the JVM from caching results between iterations. Use `mapToInt()` to avoid boxing overhead in the stream version.

### When to Use Streams
- **Readability**: When the pipeline is clear and concise (filter → map → collect).
- **Parallelism**: When you need parallel processing and the operation is CPU-bound.
- **Declarative code**: When you want to express what to do, not how to do it.
- **Staff insight**: Use streams when they make the code clearer. The 5-10% performance difference is negligible compared to the maintainability benefit. Avoid streams only in performance-critical paths where you've profiled and confirmed they're a bottleneck.

### Key Findings
- **Primitive streams**: `IntStream` is 2-3× faster than `Stream<Integer>` due to no boxing.
- **Terminal operations**: `sum()`, `count()` are highly optimized; close to loop performance.
- **Collectors**: `toList()` and `toMap()` add overhead; manual loop with HashMap is faster.
- **Staff insight**: The biggest performance win is using primitive streams. `IntStream.filter().sum()` is often faster than the equivalent loop because the JIT can vectorize the operation. Always prefer primitive streams when working with numeric data.
