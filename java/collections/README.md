# Java Collections

## Overview

Java Collections Framework provides data structures and algorithms. For staff engineers, choosing the right collection is about **time/space complexity**, **thread safety**, **memory overhead**, and **iteration patterns**.

## Interfaces & Implementations

### List
| Implementation | Time Complexity | Use Case | Staff Insight |
|---------------|----------------|----------|---------------|
| **ArrayList** | O(1) get/set; O(n) insert/delete | General purpose; random access | Default choice; grows by 50% on resize |
| **LinkedList** | O(n) get; O(1) insert/delete at ends | Frequent insert/delete at ends | Rarely better than ArrayList; higher memory overhead |
| **CopyOnWriteArrayList** | O(1) get; O(n) modify | Read-heavy; iteration without ConcurrentModificationException | Expensive writes; use only when reads >> writes |

### Set
| Implementation | Time Complexity | Use Case | Staff Insight |
|---------------|----------------|----------|---------------|
| **HashSet** | O(1) add/contains/remove | Unique elements; no order | Default choice for uniqueness checks |
| **LinkedHashSet** | O(1) add/contains; insertion order | Unique elements with insertion order | Slightly higher memory; useful for LRU caches |
| **TreeSet** | O(log n) all operations | Sorted unique elements | Backed by TreeMap; use for range queries |

### Map
| Implementation | Time Complexity | Use Case | Staff Insight |
|---------------|----------------|----------|---------------|
| **HashMap** | O(1) get/put | General purpose key-value | Default choice; handles null keys |
| **LinkedHashMap** | O(1) get/put; insertion/access order | Caches (LRU); ordered iteration | Access-order mode enables LRU cache |
| **TreeMap** | O(log n) all operations | Sorted key-value; range queries | Backed by Red-Black tree; floorKey, ceilingKey |
| **ConcurrentHashMap** | O(1) get/put; thread-safe | Concurrent key-value | Segment-level locking; no null keys |
| **IdentityHashMap** | O(1) get/put; == comparison | Object identity mapping | Rarely needed; use when == matters, not equals |

### Queue/Deque
| Implementation | Time Complexity | Use Case | Staff Insight |
|---------------|----------------|----------|---------------|
| **ArrayDeque** | O(1) add/poll | General purpose queue/deque | Faster than LinkedList; no synchronization |
| **PriorityQueue** | O(log n) add/poll | Priority-based processing | Not thread-safe; min-heap by default |
| **LinkedBlockingQueue** | O(1) put/take | Producer-consumer pattern | Bounded/unbounded; thread-safe |
| **ConcurrentLinkedQueue** | O(1) add/poll; lock-free | Lock-free queue | Non-blocking; high throughput |

## HashMap Internal Working

1. **Array of buckets**: `Node<K,V>[] table` with default capacity 16
2. **Hash computation**: `hash(key.hashCode())` with bit mixing
3. **Bucket index**: `(n - 1) & hash` (power-of-2 size enables bitwise AND)
4. **Collision resolution**: Linked list → Red-Black tree (when list size > 8)
5. **Resize**: When size > loadFactor * capacity (default 0.75); doubles capacity
6. **Staff insight**: HashMap uses **treeification** (Java 8+) to avoid O(n) worst case. Attack vectors exist with crafted hash codes; use `Collections.synchronizedMap` or `ConcurrentHashMap` for production.

## Key Concepts

- **Fail-fast vs fail-safe iterators**: Fail-fast throws ConcurrentModificationException; fail-safe (CopyOnWriteArrayList) works on snapshot
- **Load factor**: Threshold for resize; default 0.75 balances time/space
- **Tree vs Hash**: Hash for O(1) average; Tree for O(log n) worst-case + sorted order
- **Staff insight**: Use **ConcurrentHashMap** over `Collections.synchronizedMap` — finer-grained locking; better throughput.

## Java 8+ Features

- **Stream API**: Declarative data processing; parallel streams for CPU-bound tasks
- **Default methods**: Interface methods with default implementation
- **computeIfAbsent/Present**: Atomic compute-and-put; avoids double-checking
- **merge function**: Atomic merge; upsert pattern
- **Staff insight**: Use **computeIfAbsent** for lazy initialization; it's atomic and avoids race conditions.

## Problems (8)

| Problem | Key Concepts |
|---------|-------------|
| [HashMap Internals](problems/hashmap-internals/) | Bucket array, hash mixing, treeification, resize |
| [ConcurrentHashMap Internals](problems/concurrent-hashmap/) | CAS + synchronized, weakly consistent iterators, computeIfAbsent |
| [LRU Cache with LinkedHashMap](problems/lru-cache-linkedhashmap/) | Access order, removeEldestEntry, Caffeine alternative |
| [TreeMap & Red-Black Tree](problems/treemap-redblack/) | Self-balancing BST, rotations, range queries |
| [Priority Queue (Binary Heap)](problems/priority-heap/) | Heapify, offer/poll, top-K selection |
| [CopyOnWriteArrayList](problems/copyonwritearraylist/) | Copy-on-write, snapshot iterator, read-heavy workloads |
| [Blocking Queue Design](problems/blocking-queue-design/) | Two-lock design, condition variables, backpressure |
| [Custom Collection Framework](problems/custom-collection/) | Decorator pattern, iterator, equals/hashCode |

## Staff-Level Collections Checklist

1. **Prefer ArrayList over LinkedList**: Better cache locality; lower memory overhead
2. **Use ConcurrentHashMap for concurrent access**: Better throughput than synchronized map
3. **Choose LinkedHashMap for LRU cache**: Access-order mode; removeEldestEntry override
4. **Use ArrayDeque over Stack/LinkedList**: Faster; no synchronization overhead
5. **Pre-size collections**: Avoid resize overhead when size is known
6. **Use computeIfAbsent for lazy init**: Atomic; avoids race conditions
7. **Avoid autoboxing in hot paths**: Primitive collections (Eclipse Collections) for performance
8. **Profile collection choices**: Use JFR to measure actual performance impact
