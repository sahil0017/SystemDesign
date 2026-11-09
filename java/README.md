# Java

Comprehensive module covering Java fundamentals, concurrency, collections, JVM internals, streams, and performance tuning. Essential for staff-level Java engineering interviews.

**References**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/), [HelloInterview](https://www.hellointerview.com/)

## Topics (5)

| Topic | Key Concepts |
|-------|-------------|
| [Concurrency](concurrency/) | Threads, locks, executors, CompletableFuture, concurrent collections, deadlocks |
| [Collections](collections/) | HashMap internals, ConcurrentHashMap, ArrayList vs LinkedList, time complexity |
| [JVM](jvm/) | Memory model, GC algorithms (G1/ZGC), JIT compilation, class loading |
| [Streams](streams/) | Intermediate/terminal operations, collectors, parallel streams, best practices |
| [Performance](performance/) | Profiling (JFR/async-profiler), GC tuning, benchmarking (JMH), I/O optimization |

## Concurrency Problems (22)

| Problem | Key Concepts |
|---------|-------------|
| [Thread Pool](problems/thread-pool/) | Worker threads, rejection policies, queue selection |
| [Producer-Consumer](problems/producer-consumer/) | BlockingQueue, wait/notify, semaphore |
| [ReadWriteLock](problems/readwritelock/) | Shared/exclusive locks, writer starvation, fairness |
| [Fair ReadWriteLock](problems/read-write-lock-fair/) | FIFO ordering, writer starvation prevention, lock downgrade |
| [Latch & Barrier](problems/latch-barrier/) | CountdownLatch, CyclicBarrier, Phaser |
| [Blocking Queue](problems/blocking-queue/) | Condition variables, circular array, interruptible |
| [Semaphore](problems/semaphore/) | Permits, fair/non-fair, resource pooling |
| [Cache with Expiry](problems/cache-expiry/) | TTL, DelayQueue, lazy + eager cleanup |
| [Rate Limiter](problems/rate-limiter/) | Token bucket, sliding window, thread safety |
| [Double-Checked Locking](problems/double-checked-locking/) | Volatile, instruction reordering, Bill Pugh pattern |
| [Actor Model](problems/actor-model/) | Message passing, mailbox, supervision, isolation |
| [Disruptor Pattern](problems/disruptor-pattern/) | Lock-free ring buffer, cache line padding, wait strategies |
| [Phaser](problems/phaser/) | Dynamic parties, multi-phase, hierarchical phasers |
| [Virtual Threads](problems/virtual-threads/) | Project Loom, pinning, migration from reactive |
| [Structured Concurrency](problems/structured-concurrency/) | Task scope, fork/join, cancellation, cleanup |
| [StampedLock](problems/stamped-lock/) | Optimistic reads, conversion, non-reentrant |
| [Lock-Free Stack](problems/lock-free-stack/) | CAS, ABA problem, memory reclamation |
| [Exchanger](problems/exchanger/) | Two-thread swap, buffer swapping, double-buffering |
| [Concurrency Fundamentals](problems/concurrency/) | Thread lifecycle, synchronization, volatile, memory model |
| [AtomicReferenceFieldUpdater](problems/atomic-reference-field-updater/) | Lock-free field update, CAS, VarHandle |
| [CompletableFuture Advanced](problems/completion-advanced/) | Async composition, retry, timeout, fallback |

## Collections Problems (8)

| Problem | Key Concepts |
|---------|-------------|
| [HashMap Internals](collections/problems/hashmap-internals/) | Bucket array, hash mixing, treeification, resize |
| [ConcurrentHashMap](collections/problems/concurrent-hashmap/) | CAS + synchronized, weakly consistent iterators |
| [LRU Cache](collections/problems/lru-cache-linkedhashmap/) | Access order, removeEldestEntry, Caffeine |
| [TreeMap & Red-Black Tree](collections/problems/treemap-redblack/) | Self-balancing BST, rotations, range queries |
| [Priority Queue](collections/problems/priority-heap/) | Heapify, offer/poll, top-K selection |
| [CopyOnWriteArrayList](collections/problems/copyonwritearraylist/) | Copy-on-write, snapshot iterator |
| [Blocking Queue Design](collections/problems/blocking-queue-design/) | Two-lock design, condition variables |
| [Custom Collection](collections/problems/custom-collection/) | Decorator pattern, iterator, equals/hashCode |

## JVM Problems (8)

| Problem | Key Concepts |
|---------|-------------|
| [Memory Leak Detection](jvm/problems/memory-leak-detection/) | Heap dumps, MAT, GC root tracing |
| [GC Tuning](jvm/problems/gc-tuning-strategies/) | G1/ZGC selection, pause time target |
| [Custom ClassLoader](jvm/problems/custom-classloader/) | Delegation model, hot reloading |
| [JIT Optimization](jvm/problems/jit-optimization/) | Inlining, escape analysis, tiered compilation |
| [Thread Dump Analysis](jvm/problems/thread-dump-analysis/) | Thread states, deadlock detection |
| [Heap Dump Analysis](jvm/problems/heap-dump-analysis/) | MAT analysis, dominator tree |
| [OOM Prevention](jvm/problems/oom-prevention/) | Heap sizing, monitoring, graceful degradation |
| [JVM Startup Optimization](jvm/problems/jvm-startup-optimization/) | AppCDS, lazy init, GraalVM Native Image |

## Performance Problems (8)

| Problem | Key Concepts |
|---------|-------------|
| [Connection Pool](performance/problems/connection-pool/) | Borrow/return, validation, HikariCP |
| [Object Pool](performance/problems/object-pool/) | ThreadLocal pooling, state reset |
| [Caffeine Cache](performance/problems/caffeine-cache/) | Window TinyLFU, async loading |
| [JMH Benchmark](performance/problems/jmh-benchmark/) | Warm-up, Blackhole, forks |
| [Async I/O Server](performance/problems/async-io-server/) | Netty event loop, zero-copy |
| [Batch Processing](performance/problems/batch-processor/) | Chunk processing, checkpointing |
| [String Optimization](performance/problems/string-optimization/) | StringBuilder, interning |
| [Memory Profiler](performance/problems/memory-profiler/) | JFR allocation tracking, sampling |

## Streams Problems (6)

| Problem | Key Concepts |
|---------|-------------|
| [Custom Collector](streams/problems/custom-collector/) | Supplier, accumulator, combiner |
| [Pipeline Optimization](streams/problems/stream-pipeline-optimization/) | Lazy evaluation, short-circuiting |
| [Parallel Stream Tuning](streams/problems/parallel-stream-tuning/) | ForkJoinPool, work stealing |
| [Stream vs Loop](streams/problems/stream-vs-loop/) | JMH comparison, primitive streams |
| [Data Aggregation](streams/problems/data-aggregation/) | groupingBy, downstream collectors |
| [Reactive Stream](streams/problems/reactive-stream/) | Backpressure, Publisher/Subscriber |

## Concurrency Design Problems (6)

| Problem | Key Concepts |
|---------|-------------|
| [Deadlock Detector](concurrency/problems/deadlock-detector/) | Wait-for graph, DFS cycle detection |
| [Thread-Safe Singleton](concurrency/problems/thread-safe-singleton/) | Bill Pugh, enum, double-checked locking |
| [Event Loop](concurrency/problems/event-loop/) | Selector, task queue, non-blocking I/O |
| [Work Stealing Pool](concurrency/problems/work-stealing-pool/) | Per-thread deque, CAS, fork/join |
| [Read-Write Cache](concurrency/problems/read-write-cache/) | StampedLock, optimistic reads |
| [Async Pipeline](concurrency/problems/async-pipeline/) | Stage chaining, backpressure |

## How to Use

1. **Start with topics**: Read each topic to understand Java fundamentals
2. **Practice concurrency problems**: Implement each problem to master thread-safe design
3. **Explore collections**: Understand HashMap, ConcurrentHashMap, and custom collection design
4. **Master JVM internals**: Learn memory management, GC tuning, and profiling techniques
5. **Optimize performance**: Study connection pooling, caching, benchmarking, and async I/O
6. **Master streams**: Learn pipeline optimization, parallel streams, and reactive programming
7. **Cross-reference**: Relate to LLD concurrency problems and blogs on Java concurrency
