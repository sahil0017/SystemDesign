# LLD Concurrency Problems

This submodule contains **Low-Level Design problems with a concurrency focus**, sourced from [LLD Coding](https://www.lldcoding.com/) and [AlgoMaster](https://algomaster.io/). Each problem requires designing thread-safe systems that handle concurrent access, synchronization, and coordination.

## Problems

| # | Problem | Key Concurrency Concepts | Reference |
|---|---------|--------------------------|-----------|
| 1 | [Bank Transaction](bank-transaction/) | Lock ordering, ReadWriteLock, AtomicLong, deadlock prevention | LLD Coding |
| 2 | [Train Deadlock](train-deadlock/) | Lock ordering, try-lock with timeout, rollback, semaphore | LLD Coding |
| 3 | [Traffic Light](traffic-light/) | State pattern, ScheduledExecutorService, volatile, interrupt | LLD Coding |
| 4 | [Call Center Queue](call-center-queue/) | PriorityBlockingQueue, BlockingQueue, DelayQueue, LongAdder | LLD Coding |
| 5 | [Online Matchmaking](online-matchmaking/) | ConcurrentHashMap, CAS, DelayQueue, atomic state transition | LLD Coding |
| 6 | [Multiplayer Game Sync](multiplayer-game-sync/) | Copy-on-write, ConcurrentLinkedQueue, CyclicBarrier, CRDTs | LLD Coding |
| 7 | [Thread-Safe Cache with TTL](thread-safe-cache/) | ConcurrentHashMap, DelayQueue, lazy + eager expiration | AlgoMaster |
| 8 | [Concurrent HashMap](concurrent-hashmap/) | Segment locking, CAS, striped counters, tree bins | AlgoMaster |
| 9 | [Thread-Safe Blocking Queue](thread-safe-blocking-queue/) | Condition variables, spurious wakeups, ReentrantLock | AlgoMaster |
| 10 | [Concurrent Bloom Filter](concurrent-bloom-filter/) | AtomicLongArray, double hashing, lock-free reads | AlgoMaster |
| 11 | [Thread Pool](thread-pool/) | BlockingQueue, rejection policies, graceful shutdown | LLD Coding |
| 12 | [Delivery Truck Loading](delivery-truck-loading/) | Fine-grained locking, CAS, bin packing | LLD Coding |
| 13 | [Rocket Launch Countdown](rocket-launch-countdown/) | CountDownLatch, CyclicBarrier, CompletableFuture, CAS | LLD Coding |
| 14 | [Jigsaw Puzzle Builder](jigsaw-puzzle-builder/) | Per-cell locking, CAS, CountDownLatch | LLD Coding |
| 15 | [Warehouse Packing](warehouse-packing/) | Per-box locking, CAS, 3D bin packing | LLD Coding |

## Key Concurrency Patterns

- **Lock ordering**: Prevent deadlocks by acquiring locks in a consistent global order
- **Compare-And-Swap (CAS)**: Lock-free atomic operations for single-variable updates
- **Fine-grained locking**: Per-resource locks instead of global locks for higher throughput
- **Condition variables**: Precise signaling between threads (notFull/notEmpty)
- **Barrier primitives**: CountDownLatch (one-shot), CyclicBarrier (reusable) for thread coordination
- **Copy-on-write**: Immutable snapshots for lock-free reads
- **Striped counters**: LongAdder for high-contentment metric collection
