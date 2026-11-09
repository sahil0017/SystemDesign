# Heap Dump Analysis

## Problem Statement

Design a systematic approach to analyzing Java heap dumps to identify memory leaks, large object retention, and abnormal memory usage patterns using tools like Eclipse MAT and JFR.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Heap dump capture**: Generate heap dumps using jmap, jcmd, or automatic OOM trigger.
- **Dominator tree analysis**: Find largest objects and their retention chains.
- **Histogram analysis**: Count and size of objects per class.
- **GC root tracing**: Trace reference paths from GC roots to suspected leaked objects.
- **Comparison analysis**: Compare two heap dumps to identify growing object sets.

### Non-Functional Requirements
- **Production safety**: Minimize impact of heap dump capture on running application.
- **Scalability**: Handle large heap dumps (10GB+) efficiently.
- **Automation**: Automated heap dump capture and analysis in CI/CD pipelines.

## Key Design Decisions
- **jcmd for capture**: `jcmd <pid> GC.heap_dump` — safer than jmap; doesn't hang the JVM.
- **MAT for analysis**: Eclipse Memory Analyzer Tool for dominator tree, leak suspects, and OQL queries.
- **Live heap dump**: Only dump reachable objects (`jmap -dump:live`) to reduce noise.
- **Baseline comparison**: Compare heap dumps from healthy vs problematic states.

## Staff-Level Design Considerations

### Heap Dump Capture Strategies
- **On OOM**: `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/path/to/dumps` — automatic capture.
- **On demand**: `jcmd <pid> GC.heap_dump /path/to/heap.hprof` — manual capture.
- **Periodic**: Use JFR or custom code to capture periodic snapshots for trend analysis.
- **Staff insight**: Always configure automatic heap dump on OOM in all environments. Without it, diagnosing an OOM incident is nearly impossible since the JVM crashes before you can capture a dump.

### MAT Analysis Techniques
- **Leak Suspects Report**: MAT's automatic analysis identifies potential leak sources with confidence scores.
- **Dominator Tree**: Shows which objects retain the most memory. The dominator of an object is the unique object through which it's reachable from GC roots.
- **Path to GC Root**: Shows the shortest reference chain from a GC root to the selected object. Use "Exclude weak/soft references" to find strong retention paths.
- **OQL (Object Query Language)**: SQL-like queries to search for specific objects or patterns.
- **Staff insight**: The dominator tree is the most powerful feature in MAT. It shows not just what's large, but what's retaining what. Focus on the top 5 dominators — they usually account for 80% of heap usage.

### Common Memory Patterns
- **Large array retention**: Single large array (e.g., byte[]) retained by a long-lived object.
- **Collection growth**: HashMap/ArrayList growing beyond expected size due to missing eviction.
- **Class loader leaks**: Multiple instances of the same ClassLoader, each retaining its class set.
- **Thread stack growth**: Excessive thread creation with large stack sizes.
- **Native memory**: DirectByteBuffers and off-heap memory not visible in heap dumps.
- **Staff insight**: If you see multiple ClassLoader instances in the dominator tree, you likely have a class loader leak. This is common in plugin systems and web containers that don't properly unload classes.

### Comparison Analysis
- **Two heap dumps**: Take one dump during normal operation and one during the issue.
- **MAT comparison**: Use "Compare to Heapwalk" to find objects that grew between dumps.
- **Focus on growth**: Objects that grew significantly between dumps are the most likely leak candidates.
- **Staff insight**: Single heap dump analysis is often inconclusive. Comparing two dumps (before and during the issue) dramatically improves leak detection accuracy by showing what changed.
