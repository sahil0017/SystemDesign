# Deadlock Detector

## Problem Statement

Design a deadlock detection system that monitors thread lock acquisition patterns and identifies circular dependencies (deadlocks) in real-time, reporting the involved threads and locks.

**Reference**: [AlgoMaster](https://algomaster.io/), [HelloInterview](https://www.hellointerview.com/)

## Requirements

### Functional Requirements
- **Lock tracking**: Record which thread holds which lock and which thread waits for which lock.
- **Wait-for graph**: Build a directed graph where edges represent "thread A waits for thread B's lock."
- **Cycle detection**: Detect cycles in the wait-for graph using DFS.
- **Reporting**: Report deadlocked threads, locks, and stack traces.
- **Prevention**: Suggest lock ordering to prevent future deadlocks.

### Non-Functional Requirements
- **Low overhead**: Detection should add minimal overhead to lock operations.
- **Real-time**: Detect deadlocks as they occur, not after the fact.
- **Accuracy**: No false positives; only report actual deadlocks.

## Key Design Decisions
- **Wait-for graph**: Directed graph where nodes are threads and edges represent wait relationships.
- **DFS cycle detection**: Standard algorithm to find cycles in directed graphs.
- **Instrumentation**: Wrap lock acquisition/release to track state.
- **Periodic check**: Run cycle detection periodically or on lock acquisition timeout.

## Staff-Level Design Considerations

### Wait-For Graph
- **Nodes**: Each thread is a node in the graph.
- **Edges**: Thread A → Thread B means A is waiting for a lock held by B.
- **Deadlock**: A cycle in the graph means a deadlock exists.
- **Staff insight**: The wait-for graph is the standard algorithm for deadlock detection in operating systems and databases. Java's `ThreadMXBean.findDeadlockedThreads()` uses this approach internally.

### Cycle Detection Algorithm
```java
// DFS-based cycle detection
boolean hasCycle(Thread node, Set<Thread> visited, Set<Thread> recursionStack) {
    visited.add(node);
    recursionStack.add(node);
    for (Thread neighbor : waitForGraph.get(node)) {
        if (!visited.contains(neighbor) && hasCycle(neighbor, visited, recursionStack))
            return true;
        if (recursionStack.contains(neighbor))
            return true;  // Cycle found
    }
    recursionStack.remove(node);
    return false;
}
```
- **Staff insight**: DFS cycle detection is O(V + E) where V = threads and E = wait relationships. For most applications, this is fast enough to run on every lock acquisition.

### Deadlock Prevention Strategies
- **Lock ordering**: Always acquire locks in a consistent global order.
- **tryLock with timeout**: Use `ReentrantLock.tryLock(timeout)` instead of `lock()`.
- **Lock-free data structures**: Use `ConcurrentHashMap`, `AtomicReference`, etc.
- **Reduce lock scope**: Minimize the code executed while holding a lock.
- **Staff insight**: The best deadlock prevention strategy is lock ordering. Define a global order for all locks and always acquire them in that order. This makes deadlocks impossible by construction.

### Common Pitfalls
- **Instrumentation overhead**: Tracking every lock operation adds overhead; sample in production.
- **False positives**: Transient wait cycles that resolve quickly are not deadlocks.
- **Missing locks**: Synchronized blocks and ReentrantLocks need different instrumentation.
- **Staff insight**: Java's `ThreadMXBean.findDeadlockedThreads()` already provides deadlock detection. Use it in production monitoring instead of building a custom detector. Enable it with periodic checks in your health monitoring system.
