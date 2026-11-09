# Java Performance

## Overview

Java performance tuning and optimization techniques. For staff engineers, performance is about **measuring before optimizing**, **understanding bottlenecks**, and **making trade-offs** between readability, maintainability, and speed.

## Profiling Tools

| Tool | Type | Overhead | Use Case | Staff Insight |
|------|------|----------|----------|---------------|
| **JFR (Java Flight Recorder)** | Production profiler | <1% | Production profiling; low overhead | Default choice for production; built into JDK |
| **JMC (Java Mission Control)** | JFR analyzer | N/A | Analyze JFR recordings; flame graphs | Use with JFR for production debugging |
| **async-profiler** | Sampling profiler | <1% | CPU profiling; flame graphs | Best for CPU bottleneck identification |
| **VisualVM** | All-in-one | Medium | Development profiling; memory analysis | Good for development; not for production |
| **JProfiler** | Commercial | Medium | Comprehensive profiling; memory, CPU, threads | Enterprise-grade; expensive |
| **YourKit** | Commercial | Medium | Comprehensive profiling; database monitoring | Enterprise-grade; good DB profiling |

## Performance Areas

### Memory
- **Object allocation**: Short-lived objects in Eden; cheap with TLAB (Thread Local Allocation Buffer)
- **Memory leaks**: Unbounded collections, static references, unclosed resources; use heap dump analysis
- **GC tuning**: G1 GC defaults are good; tune only when pauses exceed SLA
- **Memory pooling**: Object reuse for high-allocation paths; avoid premature pooling
- **Staff insight**: **Allocation is cheap** in Java. Focus on reducing GC pressure, not allocation count. Use TLAB for thread-local allocation.

### CPU
- **Hotspot identification**: Profile with async-profiler; find top 5 methods by CPU time
- **Algorithm optimization**: O(n log n) vs O(n²); choose right data structure
- **Cache locality**: Sequential access > random access; prefer arrays over linked structures
- **Vectorization**: SIMD operations; Java 16+ vector API (incubator)
- **Staff insight**: **90% of CPU time is in 10% of code** (Pareto principle). Profile first; optimize hotspots.

### I/O
- **Buffered I/O**: BufferedReader/BufferedWriter; reduce system calls
- **NIO and channels**: Non-blocking I/O; Selector for multiplexing; Netty for production
- **Zero-copy techniques**: FileChannel.transferTo; sendfile; reduce memory copies
- **Connection pooling**: HikariCP for DB; Apache HttpClient for HTTP; reuse connections
- **Staff insight**: **I/O is the #1 bottleneck** in most applications. Use async I/O (Netty) for high-throughput services.

## Optimization Techniques

- **Object pooling**: Reuse expensive objects; avoid for short-lived objects
- **String optimization**: StringBuilder for concatenation; String.valueOf() for primitives
- **Lazy initialization**: Defer expensive computation until needed; double-checked locking
- **Caching strategies**: LRU cache (LinkedHashMap); Caffeine for in-memory; Redis for distributed
- **Batch processing**: Bulk operations; reduce round-trips; process in chunks
- **Staff insight**: **Premature optimization is the root of all evil**. Measure first; optimize hotspots; keep code readable.

## Benchmarking

- **JMH (Java Microbenchmark Harness)**: Proper warm-up; JIT compilation; statistical significance
- **Warm-up iterations**: Allow JIT to compile hot methods; avoid measuring interpreted code
- **Blackhole**: Consume results to prevent JIT optimization; `Blackhole.consume(result)`
- **Staff insight**: **Never use System.nanoTime() for benchmarks**. Use JMH with proper warm-up, iterations, and forks.

## Problems (8)

| Problem | Key Concepts |
|---------|-------------|
| [Connection Pool Design](problems/connection-pool/) | Borrow/return, validation, HikariCP best practices |
| [Object Pool Design](problems/object-pool/) | ThreadLocal pooling, state reset, bounded pool |
| [Caffeine Cache Design](problems/caffeine-cache/) | Window TinyLFU, async loading, cache stampede |
| [JMH Benchmark Design](problems/jmh-benchmark/) | Warm-up, Blackhole, forks, statistical significance |
| [Async I/O Server Design](problems/async-io-server/) | Netty event loop, zero-copy, non-blocking handlers |
| [Batch Processing Design](problems/batch-processor/) | Chunk processing, parallel execution, checkpointing |
| [String Optimization](problems/string-optimization/) | StringBuilder, interning, String.format overhead |
| [Memory Profiler Design](problems/memory-profiler/) | JFR allocation tracking, sampling, leak detection |

## Staff-Level Performance Checklist

1. **Profile before optimizing**: Use JFR/async-profiler to identify actual bottlenecks
2. **Use JMH for benchmarks**: Proper warm-up; statistical significance; avoid micro-optimizations
3. **Focus on I/O first**: I/O is the #1 bottleneck; use async I/O and connection pooling
4. **Avoid premature optimization**: Keep code readable; optimize only when measured
5. **Use Caffeine for in-memory caching**: Best-performing Java cache; LRU/LFU eviction
6. **Monitor GC in production**: Use JFR for low-overhead GC monitoring
7. **Tune thread pool sizes**: CPU-bound = N cores; IO-bound = N * (1 + wait/compute ratio)
8. **Use connection pooling**: HikariCP for DB; reuse HTTP connections; avoid connection creation overhead
