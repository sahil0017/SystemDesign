# Java Memory Model

## Overview

The Java Memory Model (JMM) defines how threads interact through memory. It specifies the rules for visibility, ordering, and atomicity of memory operations across threads — the foundation of correct concurrent Java programs.

## Key Concepts

### Happens-Before Relationship
If operation A happens-before operation B, then A's effects are visible to B:
- **Program order**: Each action happens-before every action that follows it in program order
- **Monitor lock**: Unlock happens-before every subsequent lock on the same monitor
- **Volatile**: Write to volatile variable happens-before every subsequent read
- **Thread start**: Thread.start() happens-before every action in the started thread
- **Thread termination**: Every action happens-before Thread.join() returns
- **Transitivity**: If A happens-before B and B happens-before C, then A happens-before C

### Visibility Problem
```java
// Thread 1              // Thread 2
running = true;          while (!running) { }  // May loop forever!
```
Without synchronization, Thread 2 may never see Thread 1's write to `running` due to CPU caching and compiler optimizations.

### Solutions
```java
// 1. Volatile
volatile boolean running = false;

// 2. Synchronized
synchronized(lock) { running = true; }

// 3. Atomic variables
AtomicBoolean running = new AtomicBoolean(false);
```

## Volatile Keyword

### Guarantees
- **Visibility**: Write is immediately visible to all threads
- **Ordering**: Prevents reordering of volatile reads/writes with other operations
- **NOT atomic**: `volatile++` is still not atomic (read-modify-write)

### When to Use
- **Flags**: Status flags, shutdown signals
- **One-time publication**: Publishing immutable objects
- **Safe publication**: Making objects visible without synchronization

### When NOT to Use
- **Compound operations**: `count++`, `if (!map.containsKey(key)) map.put(...)`
- **Invariants**: Operations that depend on multiple variables
- **Performance-critical paths**: Volatile has memory barrier overhead

## Synchronized Keyword

### Monitor Lock
- Every object has an intrinsic lock (monitor)
- Only one thread can hold the lock at a time
- Unlock flushes writes to main memory; lock reads from main memory

### Best Practices
- **Lock on private final object**: Avoid deadlocks from external lock access
- **Minimize lock scope**: Hold locks for the shortest time possible
- **Prefer concurrent collections**: Over manual synchronization

## Staff-Level Insights

### Double-Checked Locking
```java
// WRONG (pre-Java 5)
if (instance == null) {  // Not volatile, may see partially constructed object
    synchronized (lock) {
        if (instance == null) {
            instance = new Singleton();
        }
    }
}

// CORRECT (Java 5+)
private static volatile Singleton instance;
if (instance == null) {  // Volatile prevents reordering
    synchronized (lock) {
        if (instance == null) {
            instance = new Singleton();
        }
    }
}
```
- **Staff insight**: Prefer `enum` or `static initializer` for singletons — they're inherently thread-safe without volatile or synchronization.

### Effective Finality
- Local variables that aren't modified after assignment are **effectively final**
- JVM can cache effectively final variables in registers
- **Staff insight**: Declare variables `final` whenever possible — it enables compiler optimizations and makes code reasoning easier.

### False Sharing
- Two threads updating different variables on the same cache line cause cache invalidation
- **Solution**: Pad variables with unused fields to ensure they're on different cache lines
- **Staff insight**: Use `@Contended` annotation (Java 8+) to prevent false sharing in hot data structures like counters.
