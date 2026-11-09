# Memory Profiler Design

## Problem Statement

Design a memory profiler that tracks object allocations, identifies allocation hotspots, and detects memory leaks by monitoring allocation rate, object lifetime, and GC behavior in a running Java application.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Allocation tracking**: Record object allocations with class name, size, and stack trace.
- **Hotspot identification**: Find methods that allocate the most memory.
- **Leak detection**: Identify objects that outlive their expected lifetime.
- **GC correlation**: Correlate allocation patterns with GC events.
- **Reporting**: Generate reports with top allocators, retention paths, and trends.

### Non-Functional Requirements
- **Low overhead**: Profiling should add <5% overhead to application performance.
- **Production safe**: Can be enabled in production without crashing the application.
- **Scalability**: Handle high allocation rates (100K+ allocations/sec).

## Key Design Decisions
- **JFR (Java Flight Recorder)**: Built-in low-overhead profiling; <1% overhead.
- **Allocation sampling**: Sample allocations instead of tracking every one; reduces overhead.
- **Stack trace capture**: Record allocation stack traces for hotspot identification.
- **Periodic snapshots**: Capture memory state at intervals for trend analysis.

## Staff-Level Design Considerations

### JFR for Memory Profiling
- **Events**: `jdk.ObjectAllocationInNewTLAB`, `jdk.ObjectAllocationOutsideTLAB`, `jdk.GCPause`.
- **Enable**: `-XX:StartFlightRecording=duration=60s,filename=recording.jfr,settings=profile`.
- **Analysis**: Use JMC (Java Mission Control) to analyze recordings.
- **Staff insight**: JFR is the best tool for production memory profiling. It uses ring buffers and sampling to achieve <1% overhead. Unlike traditional profilers that instrument every allocation, JFR samples allocations statistically.

### Allocation Sampling Strategy
- **Sample rate**: Track 1 in N allocations; N=1000 for high-allocation applications.
- **Stack depth**: Capture top 10 frames of allocation stack trace.
- **Aggregation**: Group allocations by class name and method for hotspot identification.
- **Staff insight**: Sampling is essential for high-allocation applications. Tracking every allocation adds 10-50% overhead. Sampling 1 in 1000 allocations still provides accurate hotspot identification with <1% overhead.

### Memory Leak Detection
- **Growth detection**: Track object count per class over time; alert on steady growth.
- **Retention analysis**: Use heap dump comparison to find objects retained between snapshots.
- **GC correlation**: If allocation rate is stable but heap grows, objects are not being collected.
- **Staff insight**: The key signal for a memory leak is steady heap growth despite stable allocation rate. If the application allocates the same amount of memory per request but heap usage keeps growing, objects are being retained by long-lived references.

### Common Pitfalls
- **Full allocation tracking**: Tracking every allocation adds excessive overhead; use sampling.
- **Ignoring TLAB**: Most allocations happen in TLAB (Thread Local Allocation Buffer); they're cheap.
- **Short profiling window**: 10 seconds of profiling may miss periodic allocations; profile for 5+ minutes.
- **Staff insight**: Don't profile for too short a window. Some allocations (cache refresh, batch processing) happen periodically. Profile for at least 5 minutes to capture the full allocation pattern. Use JFR's continuous recording mode for long-term monitoring.
