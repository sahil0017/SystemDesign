# Concurrent Collections

## Overview

Java's `java.util.concurrent` package provides thread-safe collections optimized for concurrent access. Understanding when and how to use them is essential for writing performant concurrent code.

## ConcurrentHashMap

### How It Works
- **Segmented locking** (Java 7): 16 segments, each with its own lock
- **Lock striping** (Java 8+): Node-level locking using CAS operations
- **No read locks**: Reads are lock-free using volatile variables

```java
ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

// Thread-safe operations
map.put("key", 1);
map.get("key");           // Lock-free read
map.computeIfAbsent("key", k -> expensiveComputation(k));  // Atomic compute
map.merge("key", 1, Integer::sum);  // Atomic merge
```

### Key Methods
- `computeIfAbsent()`: Atomic check-and-insert
- `compute()`: Atomic compute with existing value access
- `merge()`: Atomic merge with existing value
- `forEach()`: Weakly consistent traversal (no ConcurrentModificationException)

## CopyOnWriteArrayList

### How It Works
- Every mutation creates a new copy of the underlying array
- Reads are lock-free and don't see mutations in progress
- **Best for**: Read-heavy workloads with rare writes

```java
CopyOnWriteArrayList<String> listeners = new CopyOnWriteArrayList<>();

// Safe iteration without ConcurrentModificationException
for (String listener : listeners) {
    listener.notify();  // Can safely add/remove during iteration
}
```

### When to Use
- Event listener lists
- Configuration that changes rarely
- Iterator-heavy scenarios

### When NOT to Use
- Write-heavy workloads — every write copies the entire array
- Large collections — copying is expensive

## ConcurrentLinkedQueue

### How It Works
- Lock-free queue using CAS operations
- Unbounded — no capacity limit
- Non-blocking — operations never wait

```java
ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("item");  // Non-blocking add
queue.poll();          // Non-blocking remove
```

## BlockingQueue Implementations

| Queue | Bounded | Use Case |
|-------|---------|----------|
| ArrayBlockingQueue | Yes | Fixed-size buffer, producer-consumer |
| LinkedBlockingQueue | Optional | Unbounded or bounded, high throughput |
| PriorityBlockingQueue | Unbounded | Priority-based processing |
| DelayQueue | Unbounded | Scheduled tasks, expiring entries |
| SynchronousQueue | No buffer | Direct handoff between threads |

```java
// Producer-Consumer pattern
BlockingQueue<String> queue = new ArrayBlockingQueue<>(1000);

// Producer
queue.put("item");  // Blocks if full

// Consumer
String item = queue.take();  // Blocks if empty
```

## Staff-Level Insights

### ConcurrentHashMap Performance
- **Read-heavy**: ConcurrentHashMap outperforms synchronized HashMap by 10-100x
- **Write-heavy**: Still better than synchronized HashMap due to fine-grained locking
- **Staff insight**: Use `computeIfAbsent()` instead of `containsKey()` + `put()` — the latter has a race condition even with ConcurrentHashMap.

### CopyOnWriteArrayList Trade-offs
- Great for **listener lists** where iteration is common and modification is rare
- **Staff insight**: If you have more than a few writes per second, don't use CopyOnWriteArrayList. The array copy on every write becomes a performance bottleneck. Use ConcurrentHashMap.newKeySet() instead for thread-safe sets.

### Weakly Consistent Iterators
- ConcurrentHashMap iterators don't throw ConcurrentModificationException
- They reflect the state of the map at some point during iteration
- **Staff insight**: Use `forEach()` with BiConsumer for bulk operations — it's optimized to traverse segments without locking and is faster than iterating entrySet().
