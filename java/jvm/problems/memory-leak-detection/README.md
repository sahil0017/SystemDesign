# Memory Leak Detection

## Problem Statement

Design a systematic approach to detecting and diagnosing memory leaks in Java applications using heap dumps, profiling tools, and code analysis techniques.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Heap dump analysis**: Capture and analyze heap dumps to identify leaked objects.
- **GC root tracing**: Trace reference paths from GC roots to leaked objects.
- **Dominator tree**: Find the largest memory consumers and their retention paths.
- **Histogram analysis**: Count instances per class to identify abnormal growth.
- **Leak detection tools**: Use JFR, JMC, MAT (Memory Analyzer Tool), and VisualVM.

### Non-Functional Requirements
- **Production safety**: Low-overhead detection that doesn't impact application performance.
- **Automation**: Automated heap dump capture on OOM or periodic snapshots.
- **Actionable insights**: Clear identification of leak source and fix recommendations.

## Key Design Decisions
- **Heap dump trigger**: `-XX:+HeapDumpOnOutOfMemoryError` for automatic capture.
- **MAT analysis**: Use Eclipse Memory Analyzer Tool for dominator tree and leak suspects.
- **JFR monitoring**: Continuous low-overhead memory monitoring in production.
- **Baseline comparison**: Compare heap dumps over time to identify growing objects.

## Staff-Level Design Considerations

### Common Memory Leak Patterns
- **Static collections**: Unbounded static HashMap/ArrayList that grows indefinitely.
- **Unclosed resources**: InputStream, Connection, ResultSet not closed in finally/try-with-resources.
- **Listener accumulation**: Event listeners registered but never unregistered.
- **ThreadLocal abuse**: ThreadLocal values not removed; threads in pool retain references.
- **Inner class references**: Non-static inner class holds implicit reference to outer class.
- **Cache without eviction**: HashMap used as cache without size limit or TTL.
- **Staff insight**: The #1 cause of memory leaks in production is unbounded collections. Always set size limits on caches and use proper eviction policies.

### Heap Dump Analysis Workflow
1. **Capture heap dump**: Use `jmap -dump:live,format=b,file=heap.hprof <pid>` or automatic OOM dump.
2. **Open in MAT**: Load heap dump in Eclipse MAT for analysis.
3. **Leak suspects**: Run MAT's automatic leak suspect report.
4. **Dominator tree**: Find largest objects and their retention paths.
5. **Histogram**: Compare class instance counts with baseline.
6. **GC root path**: Trace from GC root to leaked object to find the leak source.
- **Staff insight**: MAT's "Path to GC Root" feature is the most powerful tool for finding leak sources. It shows the exact reference chain from a GC root to the leaked object.

### Prevention Strategies
- **Code review**: Check for unclosed resources, static collections, and ThreadLocal usage.
- **Static analysis**: Use SpotBugs, PMD, or SonarQube to detect common leak patterns.
- **Monitoring**: Track heap usage over time; alert on steady growth.
- **Testing**: Use stress tests with heap dump analysis to catch leaks before production.
- **Staff insight**: Enable `-XX:+HeapDumpOnOutOfMemoryError` in all environments. In production, use JFR with low overhead to monitor memory trends and catch leaks before they cause OOM.
