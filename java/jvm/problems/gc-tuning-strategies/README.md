# GC Tuning Strategies

## Problem Statement

Design a garbage collection tuning strategy for a Java application based on workload characteristics, latency requirements, and heap size to minimize GC pause times and maximize throughput.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **GC selection**: Choose appropriate GC algorithm based on workload (G1, ZGC, Shenandoah, Parallel).
- **Heap sizing**: Configure initial and maximum heap size based on application memory needs.
- **Pause time target**: Set maximum GC pause time based on SLA requirements.
- **GC logging**: Enable and analyze GC logs for tuning decisions.
- **Monitoring**: Track GC metrics (pause time, throughput, allocation rate).

### Non-Functional Requirements
- **Low latency**: GC pauses within SLA (e.g., <100ms for interactive, <10ms for real-time).
- **High throughput**: Maximize application time vs GC time ratio.
- **Stability**: No OOM errors under normal load; predictable GC behavior.

## Key Design Decisions
- **G1 GC**: Default for most applications; region-based; configurable pause time target.
- **ZGC**: For large heaps (>32GB) with <10ms pause requirement; Java 15+.
- **Parallel GC**: For batch processing where throughput matters more than latency.
- **Heap sizing**: Set `-Xms = -Xmx` to avoid dynamic heap resizing overhead.

## Staff-Level Design Considerations

### GC Selection Matrix
| Workload | Heap Size | Latency Requirement | Recommended GC |
|----------|-----------|---------------------|----------------|
| Web service | <32GB | <200ms pause | G1 GC |
| Web service | >32GB | <100ms pause | ZGC (Java 15+) |
| Batch processing | Any | Throughput > latency | Parallel GC |
| Real-time | <16GB | <10ms pause | ZGC or Shenandoah |
| Microservice | <4GB | <200ms pause | G1 GC (defaults) |
- **Staff insight**: Start with G1 GC defaults. Tune only when GC pauses exceed your SLA. Premature GC tuning often makes things worse.

### G1 GC Tuning Parameters
- **-XX:MaxGCPauseMillis**: Target pause time (default 200ms). G1 adjusts region size to meet this target.
- **-XX:InitiatingHeapOccupancyPercent**: Heap occupancy threshold for concurrent marking (default 45%).
- **-XX:G1HeapRegionSize**: Region size (1-32MB, power of 2). Larger regions = fewer, bigger collections.
- **Staff insight**: Don't set MaxGCPauseMillis too aggressively. If G1 can't meet the target, it will prioritize pause time over throughput, causing more frequent GC.

### GC Log Analysis
- **Enable logging**: `-Xlog:gc*:file=gc.log:time,uptime,level,tags`
- **Key metrics**: Pause time distribution, heap utilization trend, allocation rate, promotion rate.
- **Tools**: GCEasy.io for visual analysis; GCViewer for local analysis.
- **Staff insight**: Look for these patterns in GC logs:
  - **Steady heap growth**: Memory leak — objects are never collected.
  - **Frequent minor GC**: High allocation rate — consider object pooling or reducing allocation.
  - **Long major GC pauses**: Old gen too full — increase heap or tune IHP.
  - **Mixed GC taking too long**: Too many regions to collect — increase region size.

### Common Pitfalls
- **Too-small heap**: Frequent GC cycles; low throughput.
- **Too-large heap**: Long GC pauses; wasted memory.
- **Ignoring GC logs**: Tuning without data is guessing.
- **Staff insight**: The most common GC mistake is setting the heap too large. A larger heap means longer GC pauses because the collector has more memory to scan. Size the heap based on actual application needs, not available memory.
