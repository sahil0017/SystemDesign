# JVM Internals

## Overview

Understanding Java Virtual Machine internals. For staff engineers, JVM knowledge is critical for **performance tuning**, **memory leak diagnosis**, **GC optimization**, and **understanding runtime behavior** in production.

## Memory Model

### Heap
- **Young Generation**: Eden + 2 Survivor spaces; new objects allocated in Eden; minor GC promotes survivors to Old Gen
- **Old Generation**: Long-lived objects; major GC; G1 divides into regions
- **Metaspace**: Class metadata; native memory; replaced PermGen in Java 8; auto-resizes
- **Staff insight**: Monitor **GC pause times** and **heap utilization**. Use `-XX:+HeapDumpOnOutOfMemoryError` for production debugging.

### Stack
- **Thread stacks**: Each thread has its own stack; stores local variables, method calls, return addresses
- **Frame structure**: Local variables, operand stack, reference to runtime constant pool
- **StackOverflowError**: Deep recursion or large local arrays exhaust stack space
- **Staff insight**: Default stack size is 1MB. Increase with `-Xss` for deep recursion; decrease to fit more threads.

### Direct Memory
- **Off-heap memory**: Used by NIO (ByteBuffer.allocateDirect); not managed by GC
- **Staff insight**: Direct memory bypasses GC but adds allocation overhead. Use for **network I/O** and **file I/O** where zero-copy matters.

## Garbage Collection

### GC Algorithms

| GC | Type | Pause Time | Throughput | Use Case | Staff Insight |
|----|------|-----------|------------|----------|---------------|
| **Serial GC** | Single-threaded | High | Low | Small apps; single-core | Default for client VM; not for servers |
| **Parallel GC** | Multi-threaded | Medium | High | Batch processing; throughput-critical | Default for server VM (Java 8); good for batch |
| **G1 GC** | Region-based | Configurable | High | General purpose; latency-sensitive | Default since Java 9; target pause time with `-XX:MaxGCPauseMillis` |
| **ZGC** | Concurrent | <10ms | High | Large heaps (>1TB); ultra-low latency | Java 15+; scalable to 16TB heaps |
| **Shenandoah** | Concurrent | <10ms | High | Large heaps; low latency | Red Hat contribution; similar to ZGC |

### GC Tuning
- **Heap size**: `-Xms` (initial), `-Xmx` (max); set equal to avoid resize overhead
- **GC log analysis**: `-Xlog:gc*:file=gc.log:time,uptime,level,tags`; use GCViewer/GCEasy
- **Tuning parameters**: `-XX:MaxGCPauseMillis`, `-XX:G1HeapRegionSize`, `-XX:InitiatingHeapOccupancyPercent`
- **Staff insight**: **Don't tune GC prematurely**. Profile first with JFR/JMC. Start with G1 GC defaults; tune only when pauses exceed SLA.

## Class Loading

- **Bootstrap classloader**: Loads core Java classes (`java.lang.*`, `java.util.*`)
- **Platform classloader**: Loads Java platform classes (replaced Extension classloader in Java 9)
- **Application classloader**: Loads application classes from classpath
- **Custom classloaders**: Isolated class loading (OSGi, Tomcat, plugins)
- **Delegation model**: Child delegates to parent first; prevents duplicate loading
- **Staff insight**: Class loading issues cause `ClassNotFoundException` and `NoClassDefFoundError`. Use `-verbose:class` to debug.

## JIT Compilation

- **Interpreted vs compiled**: JVM interprets bytecode; JIT compiles hot methods to native code
- **HotSpot detection**: Method invocation counter; back-edge counter for loops
- **Tiered compilation**: C1 (fast, simple) → C2 (slow, aggressive optimization)
- **Optimizations**: Inlining, escape analysis, lock elimination, array bounds check elimination
- **Staff insight**: Use `-XX:+PrintCompilation` to see JIT compilation. Warm-up time matters for benchmarks — use JMH with proper warm-up iterations.

## Problems (8)

| Problem | Key Concepts |
|---------|-------------|
| [Memory Leak Detection](problems/memory-leak-detection/) | Heap dumps, MAT, GC root tracing, dominator tree |
| [GC Tuning Strategies](problems/gc-tuning-strategies/) | G1/ZGC selection, pause time target, GC log analysis |
| [Custom ClassLoader](problems/custom-classloader/) | Delegation model, hot reloading, class isolation |
| [JIT Optimization](problems/jit-optimization/) | Inlining, escape analysis, lock elimination, tiered compilation |
| [Thread Dump Analysis](problems/thread-dump-analysis/) | Thread states, deadlock detection, CPU profiling |
| [Heap Dump Analysis](problems/heap-dump-analysis/) | MAT analysis, dominator tree, comparison analysis |
| [OOM Prevention](problems/oom-prevention/) | Heap sizing, monitoring, graceful degradation |
| [JVM Startup Optimization](problems/jvm-startup-optimization/) | AppCDS, lazy init, GraalVM Native Image |

## Staff-Level JVM Checklist

1. **Set -Xms = -Xmx**: Avoid heap resize overhead in production
2. **Use G1 GC by default**: Good balance of throughput and latency
3. **Enable heap dump on OOM**: `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/path`
4. **Monitor GC with JFR**: Low-overhead profiling; analyze with JMC
5. **Use JMH for benchmarks**: Proper warm-up; avoid JIT warm-up bias
6. **Profile before optimizing**: Use async-profiler for CPU profiling
7. **Understand memory leaks**: Use MAT (Memory Analyzer Tool) for heap dump analysis
8. **Tune thread pool sizes**: CPU-bound = N cores; IO-bound = N * (1 + wait/compute ratio)
