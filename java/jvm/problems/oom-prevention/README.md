# OOM Prevention

## Problem Statement

Design a comprehensive strategy to prevent OutOfMemoryError (OOM) in Java applications through proper heap sizing, memory monitoring, leak prevention, and graceful degradation under memory pressure.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Heap sizing**: Configure appropriate heap size based on application memory profile.
- **Memory monitoring**: Track heap usage, GC activity, and allocation rate in real time.
- **Leak prevention**: Code review and static analysis to catch common leak patterns.
- **Graceful degradation**: Reduce memory usage under pressure (cache eviction, request rejection).
- **Alerting**: Configure alerts for memory usage thresholds and GC anomalies.

### Non-Functional Requirements
- **Availability**: No OOM crashes under normal and peak load.
- **Predictability**: Stable memory usage with no unexpected growth.
- **Recoverability**: Application can recover from memory pressure without restart.

## Key Design Decisions
- **Heap sizing**: Set `-Xms = -Xmx` to avoid dynamic resizing; size based on profiling, not guessing.
- **Monitoring**: Use JFR for low-overhead production monitoring; Prometheus/JMX for metrics.
- **Caching**: Use bounded caches with eviction (Caffeine) instead of unbounded HashMaps.
- **Backpressure**: Reject or queue requests when memory usage exceeds threshold.

## Staff-Level Design Considerations

### Types of OOM and Their Causes
- **Java heap space**: Most common; unbounded collections, memory leaks, or insufficient heap.
- **Metaspace**: Too many classes loaded; common in dynamic code generation (CGLIB, Lambda, reflection).
- **GC overhead limit exceeded**: GC spends >98% of time reclaiming <2% of heap; severe memory pressure.
- **Unable to create native thread**: OS limit on threads; thread pool too large or thread leak.
- **Direct buffer memory**: NIO direct buffers exceed `-XX:MaxDirectMemorySize` limit.
- **Staff insight**: "GC overhead limit exceeded" is often more dangerous than "Java heap space" because it means the application is still running but making no progress — all CPU time is spent in GC.

### Prevention Strategies
- **Profile first**: Run load tests and measure actual memory usage before setting heap size.
- **Bounded caches**: Use Caffeine with max size and TTL; never use HashMap as an unbounded cache.
- **Streaming processing**: Process data in chunks/batches instead of loading everything into memory.
- **Connection pooling**: Use HikariCP with max pool size; unbounded connections exhaust memory.
- **Request size limits**: Limit HTTP request body size; reject oversized requests early.
- **Staff insight**: The #1 OOM prevention strategy is bounded data structures. Every collection, cache, and queue should have a maximum size. If it doesn't, it will grow until the application crashes.

### Monitoring and Alerting
- **JMX metrics**: Monitor `java.lang:type=Memory` for heap usage and `java.lang:type=GarbageCollector` for GC.
- **JFR events**: `jdk.GCHeapSummary`, `jdk.GCPause`, `jdk.ObjectAllocationInNewTLAB` for allocation rate.
- **Prometheus**: Export JMX metrics via JMX Exporter; alert on heap usage >80% for sustained periods.
- **Staff insight**: Don't alert on instantaneous heap usage spikes — GC will reclaim memory. Alert on sustained high heap usage (>80% for 5+ minutes) or increasing GC pause times, which indicate real problems.

### Graceful Degradation
- **Cache eviction**: Aggressively evict cache entries when memory pressure is detected.
- **Request rejection**: Return 503 Service Unavailable when heap usage exceeds critical threshold.
- **Circuit breaker**: Open circuit for non-essential features to reduce memory pressure.
- **Staff insight**: Design your application to degrade gracefully under memory pressure. Instead of crashing with OOM, proactively reduce memory usage by evicting caches, rejecting non-essential requests, and opening circuit breakers. This keeps the core functionality alive during memory storms.
