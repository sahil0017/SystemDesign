# JMH Benchmark Design

## Problem Statement

Design and implement correct microbenchmarks using JMH (Java Microbenchmark Harness) that account for JIT compilation, warm-up, and statistical significance to measure code performance accurately.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Benchmark setup**: Configure JMH with proper warm-up, measurement iterations, and forks.
- **Blackhole**: Use Blackhole to consume results and prevent JIT dead-code elimination.
- **State management**: Use `@State` for shared and per-thread benchmark state.
- **Throughput/AVG time**: Measure operations per second or average time per operation.
- **Statistical analysis**: Report mean, median, and confidence intervals.

### Non-Functional Requirements
- **Accuracy**: Results reflect actual production performance, not JVM artifacts.
- **Reproducibility**: Same benchmark produces consistent results across runs.
- **Statistical significance**: Results are statistically meaningful, not noise.

## Key Design Decisions
- **JMH framework**: Industry-standard benchmarking tool; handles warm-up, JIT, and statistics.
- **Warm-up iterations**: Allow JIT to compile hot methods before measurement.
- **Forks**: Run benchmark in separate JVM processes to avoid state contamination.
- **Blackhole**: Consume benchmark results to prevent JIT from optimizing away the code.

## Staff-Level Design Considerations

### JMH Benchmark Structure
```java
@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Forks(2)
@State(ThreadScope.Benchmark)
public class MyBenchmark {
    @Benchmark
    public void testMethod(Blackhole bh) {
        bh.consume(expensiveOperation());
    }
}
```
- **Staff insight**: Always use `@Forks(2)` or more. Running in a single JVM means the benchmark benefits from previous iterations' JIT compilation, skewing results. Forks ensure each run starts with a fresh JVM.

### Common Benchmarking Mistakes
- **No warm-up**: Measuring interpreted code instead of JIT-compiled code. Results are 10-100× slower.
- **Dead code elimination**: JIT removes code with no observable effect. Use `Blackhole.consume()`.
- **Constant folding**: JIT caches results of pure functions. Use `@State` with varying input.
- **Single fork**: Results are contaminated by previous benchmark methods' JIT compilation.
- **Staff insight**: Never use `System.nanoTime()` for benchmarks. The JIT compiler hasn't compiled the code, and you can't control warm-up, dead code elimination, or statistical analysis. JMH handles all of this automatically.

### Benchmark Configuration
- **Warm-up**: 5-10 iterations of 1-5 seconds each. Allows JIT to profile and compile.
- **Measurement**: 10-20 iterations of 1-5 seconds each. Collects statistically significant data.
- **Forks**: 2-3 separate JVM processes. Eliminates cross-contamination.
- **Mode**: `Throughput` (ops/sec) for capacity planning; `AverageTime` (ns/op) for latency optimization.
- **Staff insight**: For latency-sensitive code, use `Mode.AverageTime` with `@BenchmarkMode(Mode.SampleTime)` to get latency distribution (p50, p99, p999). Average time hides tail latency, which is what users experience.

### Advanced Techniques
- **Parameterized benchmarks**: `@Param({ "100", "1000", "10000" })` to test different input sizes.
- **MicroBenchmark**: Compare two implementations side by side.
- **GC measurement**: `@Group` and `@GroupBenchmark` to measure GC impact.
- **Staff insight**: Use `@Param` to benchmark different input sizes. Performance characteristics often change dramatically with input size — O(n) vs O(n²) algorithms look similar for small inputs but diverge for large ones.
