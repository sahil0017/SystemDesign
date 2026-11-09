# 🏗️ System Design Practice

> A comprehensive repository for **staff-level software engineering interview preparation**, covering HLD, LLD, Database Design, API Modeling, Distributed Systems, Java, Trade-offs, Blogs, and Books. All content is written from a **staff/principal engineer perspective** with real-world trade-offs, production insights, and scalability considerations.

## 📊 Quick Stats

| Module | Count | Description |
|--------|-------|-------------|
| [HLD](hld/) | 8 fundamentals + 8 case studies + 35 problems | System design fundamentals and real-world case studies |
| [LLD](lld/) | 4 fundamentals + 54 problems | Object-oriented design with design patterns |
| [DB Design](db-design/) | 20 problems | Relational, NoSQL, hybrid, and advanced schema design |
| [API Modeling](api-modeling/) | 3 fundamentals + 10 problems + tests | REST, gRPC, GraphQL, security, and testing |
| [Distributed Systems](distributed-systems/) | 8 topics + 20 problems (7 categories) | Kafka, Redis, ZooKeeper, consistency, and patterns |
| [Java](java/) | 5 topics + 73 problems | Concurrency, collections, JVM, streams, performance |
| [Trade-offs](tradeoffs/) | 25 trade-offs | Architectural decisions with decision frameworks |
| [Blogs & Articles](blogs-articles/) | 25 articles | Technical deep-dives across 5 categories |
| [Recommended Books](recommended-books/) | 10 books | Curated reading list with summaries |
| [Notes](notes/) | 3 resources | Interview questions, trade-offs, revision checklist |

## 🚀 Getting Started

1. **New to system design?** → Start with [HLD Fundamentals](hld/fundamentals/) and [LLD Fundamentals](lld/fundamentals/)
2. **Preparing for interviews?** → Practice [HLD Case Studies](hld/case-studies/) and [LLD Problems](lld/problems/)
3. **Leveling up to staff?** → Read [Blogs & Articles](blogs-articles/) and [Recommended Books](recommended-books/)
4. **Need a study plan?** → Check the [Revision Checklist](notes/revision-checklist.md)

## 📚 Modules

### [HLD - High-Level Design](hld/)
8 fundamentals + 8 case studies + 35 problems

### [LLD - Low-Level Design](lld/)
4 fundamentals + 54 problems (easy/medium/hard/concurrency)

### [Database Design & Data Modeling](db-design/)
20 problems (relational/NoSQL/hybrid/advanced)

### [API Modeling](api-modeling/)
3 fundamentals + 10 problems + test suite

### [Distributed Systems](distributed-systems/)
8 topics + 20 problems

### [Java](java/)
5 topics + 73 problems across 6 categories

### [Trade-offs](tradeoffs/)
25 architectural trade-offs with decision frameworks

### [Blogs & Articles](blogs-articles/)
25 technical articles across 5 categories

### [Recommended Books](recommended-books/)
10 essential books with summaries and key takeaways

### [Notes](notes/)
Interview questions, trade-offs guide, revision checklist

## HLD - High-Level Design

### Fundamentals (8 Topics)
Each topic includes staff-level insights, production trade-offs, and checklists:
- **Scalability** — vertical vs horizontal, metrics (USE/RED), auto-scaling, capacity planning
- **Load Balancing** — L4 vs L7, algorithms, health checks, global LB, session persistence
- **Caching** — multi-tier, strategies, invalidation, stampede protection, consistency models
- **Database Sharding** — strategies, shard key selection, rebalancing, cross-shard queries
- **Replication** — topologies, sync/async/semi-sync, replication lag, failover strategies
- **Consistency** — CAP/PACELC, strong/eventual/session/causal, consensus algorithms (Raft/Paxos)
- **Message Queues** — patterns, delivery semantics, ordering, backpressure, event sourcing/CQRS
- **Rate Limiting** — algorithms (token bucket, sliding window), distributed implementation, headers

### Case Studies (8 Systems)
Each case study includes **README**, **Architecture**, **API Design**, and **Database Design**:
| System | Key Concepts |
|--------|-------------|
| [URL Shortener](hld/case-studies/url-shortener/) | Base62 encoding, redirect optimization, async analytics, CDN caching |
| [WhatsApp](hld/case-studies/whatsapp/) | MQTT, Signal Protocol, presence, offline delivery, end-to-end encryption |
| [Instagram](hld/case-studies/instagram/) | Feed strategy (push/pull/hybrid), media processing, ML recommendations |
| [Uber](hld/case-studies/uber/) | Geospatial indexing (S2/H3), matching algorithm, surge pricing, real-time tracking |
| [YouTube](hld/case-studies/youtube/) | Transcoding pipeline, adaptive bitrate (HLS/DASH), multi-CDN, recommendations |
| [Notification System](hld/case-studies/notification-system/) | Multi-channel delivery, templating, rate limiting, delivery tracking |
| [E-commerce System](hld/case-studies/ecommerce-system/) | Catalog, cart, checkout, inventory (overselling prevention), payment, search |
| [Payment System](hld/case-studies/payment-system/) | Idempotency, outbox pattern, fraud detection, PCI-DSS, webhooks |

## LLD - Low-Level Design

### Fundamentals (4 Topics)
- **SOLID Principles** — with Java examples and staff-level checklist
- **Design Patterns** — creational, structural, behavioral with when-to-use guidance
- **OOP Concepts** — encapsulation, abstraction, inheritance, polymorphism, composition
- **UML Diagrams** — class, sequence, state machine, component with notation

### Practice Problems (54 Problems)
Organized by difficulty level and a dedicated concurrency category. Each problem includes staff-level problem statement, requirements, key design decisions, class diagrams, and production considerations.

**References**: [AlgoMaster](https://algomaster.io/learn/lld), [Educative.io](https://www.educative.io/), [HelloInterview](https://www.hellointerview.com/), [LLD Coding](https://www.lldcoding.com/)

#### Easy (7)
| Problem | Key Concepts |
|---------|-------------|
| [Parking Lot](lld/problems/easy/parking-lot/) | Multi-level slots, dynamic pricing, vehicle types |
| [LRU Cache](lld/problems/easy/lru-cache/) | HashMap + Doubly Linked List, O(1) operations, thread safety |
| [Snake and Ladder](lld/problems/easy/snake-and-ladder/) | Board game simulation, state management |
| [Snake Game](lld/problems/easy/snake-game/) | State machine, deque, collision detection, grid management |
| [Task Management](lld/problems/easy/task-management-system/) | State machine, search indexing, optimistic locking |
| [Tic-Tac-Toe](lld/problems/easy/tic-tac-toe/) | Game engine, win detection, state management |
| [Vending Machine](lld/problems/easy/vending-machine/) | State pattern, coin handling, product inventory |

#### Medium (18)
| Problem | Key Concepts |
|---------|-------------|
| [Stack Overflow](lld/problems/medium/stack-overflow/) | Voting, reputation system, Elasticsearch, event-driven |
| [ATM](lld/problems/medium/atm/) | State machine, strategy pattern, PIN security, ACID |
| [Logging Framework](lld/problems/medium/logging-framework/) | Chain of responsibility, async logging, rolling files |
| [Pub/Sub System](lld/problems/medium/pub-sub-system/) | Observer pattern, backpressure, delivery guarantees |
| [Car Rental](lld/problems/medium/car-rental-system/) | Double-booking prevention, dynamic pricing, state machine |
| [Hotel Management](lld/problems/medium/hotel-management-system/) | Interval tree, room state, overbooking prevention |
| [Digital Wallet](lld/problems/medium/digital-wallet/) | Double-entry bookkeeping, idempotency, fraud detection |
| [Airline Management](lld/problems/medium/airline-management-system/) | Seat map, controlled overbooking, fare classes |
| [Traffic Signal](lld/problems/medium/traffic-signal/) | State machine, emergency preemption, fail-safe design |
| [Concert Booking](lld/problems/medium/concert-ticket-booking/) | Virtual queue, seat locking, bot prevention |
| [Social Network](lld/problems/medium/social-network/) | Feed fan-out, graph storage, notification batching |
| [Elevator System](lld/problems/medium/elevator-system/) | Scheduling algorithms, request optimization |
| [Library Management](lld/problems/medium/library-management/) | Book catalog, borrowing, reservation system |
| [Splitwise](lld/problems/medium/splitwise/) | Expense splitting, debt simplification, graph algorithms |
| [Notification Service](lld/problems/medium/notification-service/) | Multi-channel delivery, templating, rate limiting |
| [Text Editor](lld/problems/medium/text-editor/) | Gap buffer, command pattern, undo/redo, OT/CRDT |
| [Movie Ticket Booking](lld/problems/medium/movie-ticket-booking/) | Seat selection, show scheduling, seat locking, payment |
| [Cricinfo Scorecard](lld/problems/medium/cricinfo-scorecard/) | Event sourcing, WebSocket, real-time stats, CQRS |
| [Chess Game](lld/problems/medium/chess-game/) | Trending topic |
| [Pub Sub](lld/problems/medium/pub-sub/) | Trending topic |

#### Hard (13)
| Problem | Key Concepts |
|---------|-------------|
| [Spotify](lld/problems/hard/spotify/) | Streaming, recommendations, playlist denormalization |
| [Amazon](lld/problems/hard/amazon/) | Microservices, inventory, CQRS, search |
| [LinkedIn](lld/problems/hard/linkedin/) | Graph queries, bidirectional BFS, feed personalization |
| [CricInfo](lld/problems/hard/cricinfo/) | Event sourcing, WebSocket, real-time stats |
| [Chess](lld/problems/hard/chess/) | Game engine, move validation, piece movement patterns |
| [Coffee Vending](lld/problems/hard/coffee-vending-machine/) | State pattern, recipe extensibility, ingredient management |
| [Restaurant](lld/problems/hard/restaurant-management/) | Kitchen workflow, bill splitting, priority queue |
| [Stock Exchange](lld/problems/hard/stock-exchange/) | Matching engine, order book, lock-free structures |
| [Course Registration](lld/problems/hard/course-registration/) | DAG prerequisites, interval tree, registration queue |
| [Movie Ticket Booking](lld/problems/hard/movie-ticket-booking/) | Seat selection, show management, payment |
| [Online Auction](lld/problems/hard/online-auction/) | Proxy bidding, time-wheel, soft close |
| [Food Delivery](lld/problems/hard/food-delivery/) | GeoHash/H3, real-time tracking, ETA estimation |
| [Ride-Sharing](lld/problems/hard/ride-sharing/) | H3 indexing, surge pricing, WebSocket tracking |

#### Concurrency (15)
Thread-safe systems requiring concurrent access, synchronization, and coordination. See [Concurrency Problems](lld/problems/concurrency/) for details.

| Problem | Key Concurrency Concepts |
|---------|--------------------------|
| [Bank Transaction](lld/problems/concurrency/bank-transaction/) | Lock ordering, ReadWriteLock, deadlock prevention |
| [Train Deadlock](lld/problems/concurrency/train-deadlock/) | Lock ordering, try-lock, rollback, semaphore |
| [Traffic Light](lld/problems/concurrency/traffic-light/) | State pattern, ScheduledExecutorService, volatile |
| [Call Center Queue](lld/problems/concurrency/call-center-queue/) | PriorityBlockingQueue, DelayQueue, LongAdder |
| [Online Matchmaking](lld/problems/concurrency/online-matchmaking/) | ConcurrentHashMap, CAS, atomic state transition |
| [Multiplayer Game Sync](lld/problems/concurrency/multiplayer-game-sync/) | Copy-on-write, ConcurrentLinkedQueue, CyclicBarrier |
| [Thread-Safe Cache with TTL](lld/problems/concurrency/thread-safe-cache/) | ConcurrentHashMap, DelayQueue, lazy + eager expiration |
| [Concurrent HashMap](lld/problems/concurrency/concurrent-hashmap/) | Segment locking, CAS, striped counters, tree bins |
| [Thread-Safe Blocking Queue](lld/problems/concurrency/thread-safe-blocking-queue/) | Condition variables, spurious wakeups, ReentrantLock |
| [Concurrent Bloom Filter](lld/problems/concurrency/concurrent-bloom-filter/) | AtomicLongArray, double hashing, lock-free reads |
| [Thread Pool](lld/problems/concurrency/thread-pool/) | BlockingQueue, rejection policies, graceful shutdown |
| [Delivery Truck Loading](lld/problems/concurrency/delivery-truck-loading/) | Fine-grained locking, CAS, bin packing |
| [Rocket Launch Countdown](lld/problems/concurrency/rocket-launch-countdown/) | CountDownLatch, CyclicBarrier, CompletableFuture |
| [Jigsaw Puzzle Builder](lld/problems/concurrency/jigsaw-puzzle-builder/) | Per-cell locking, CAS, CountDownLatch |
| [Warehouse Packing](lld/problems/concurrency/warehouse-packing/) | Per-box locking, CAS, 3D bin packing |

## Database Design & Data Modeling (20 Problems)

Comprehensive database schema design, data modeling, and storage architecture problems organized by category. See [Database Design Module](db-design/) for details.

### Relational Schema Design (6 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [E-commerce](db-design/problems/relational/ecommerce-schema/) | Products, orders, payments, inventory, reviews, promotions |
| [Social Network](db-design/problems/relational/social-network/) | Users, posts, followers, feeds, notifications, fan-out |
| [Ride-Sharing](db-design/problems/relational/ride-sharing/) | Drivers, rides, ratings, surge pricing, geospatial |
| [SaaS Multi-tenancy](db-design/problems/relational/saas-multitenancy/) | Tenant isolation, RLS, subscriptions, usage tracking |
| [Hospital Management](db-design/problems/relational/hospital-management/) | Patients, doctors, appointments, billing, HIPAA audit |
| [Content CMS](db-design/problems/relational/content-cms/) | Articles, revisions, tags, full-text search, comments |

### NoSQL Schema Design (5 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [IoT Time-Series](db-design/problems/nosql/iot-timeseries/) | Sensor data, aggregations, TTL retention, down-sampling |
| [Real-time Chat](db-design/problems/nosql/realtime-chat/) | Messages, conversations, read receipts, offline sync |
| [Session Store](db-design/problems/nosql/session-store/) | Distributed sessions, TTL, Redis clustering |
| [Product Catalog](db-design/problems/nosql/product-catalog/) | High-read catalog, denormalization, GSI filtering |
| [Clickstream Analytics](db-design/problems/nosql/clickstream-analytics/) | Event ingestion, real-time dashboards, sessionization |

### Hybrid Architecture (4 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Analytics Pipeline](db-design/problems/hybrid/analytics-pipeline/) | OLTP → Kafka → OLAP, CDC, ELT, materialized views |
| [Search Engine](db-design/problems/hybrid/search-engine/) | Full-text search, index sync, relevance tuning, autocomplete |
| [Recommendation System](db-design/problems/hybrid/recommendation-system/) | Two-phase rec, feature store, A/B testing, cold start |
| [Log Aggregation](db-design/problems/hybrid/log-aggregation/) | Log collection, ILM, hot-warm-cold tiering, alerting |

### Advanced Topics (5 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Sharding Strategy](db-design/problems/advanced/sharding-strategy/) | Shard key, virtual nodes, consistent hashing, rebalancing |
| [Data Migration](db-design/problems/advanced/data-migration/) | Zero-downtime migration, dual-write, CDC, reconciliation |
| [CDC Pipeline](db-design/problems/advanced/cdc-pipeline/) | WAL capture, exactly-once, schema evolution, monitoring |
| [Consistency Models](db-design/problems/advanced/consistency-models/) | CAP, PACELC, quorum, causal consistency, vector clocks |
| [Backup & Recovery](db-design/problems/advanced/backup-recovery/) | RPO/RTO, PITR, cross-region DR, failover testing |

## Distributed Systems (8 Topics + 20 Problems across 7 Categories)

### Topics
| Topic | Key Concepts |
|-------|-------------|
| [Kafka](distributed-systems/problems/kafka/) | Topics, partitions, producers/consumers, delivery semantics, consumer groups |
| [Redis](distributed-systems/problems/redis/) | Data structures, persistence, clustering, pub/sub, Lua scripting, Streams |
| [ZooKeeper](distributed-systems/problems/zookeeper/) | ZNodes, watches, ensemble, leader election, distributed locks |
| [Consistency Models](distributed-systems/problems/consistency-models/) | Strong, eventual, session, causal, CAP theorem, quorum-based |
| [Distributed Locks](distributed-systems/problems/distributed-locks/) | Redis SETNX/Redlock, ZooKeeper, database-based, TTL, atomic release |
| [Idempotency](distributed-systems/problems/idempotency/) | Idempotency keys, database constraints, message deduplication, TTL |
| [Saga Pattern](distributed-systems/problems/saga-pattern/) | Choreography vs orchestration, compensating transactions, event sourcing |
| [Outbox Pattern](distributed-systems/problems/outbox-pattern/) | Reliable event publishing, polling vs CDC (Debezium), idempotent consumers |

### Problems by Category (17 Problems)

#### Coordination (3) — Locks, leader election, data distribution
| Problem | Key Concepts |
|---------|-------------|
| [Distributed Lock](distributed-systems/problems/coordination/distributed-lock/) | RedLock algorithm, TTL, clock drift, watchdog |
| [Leader Election](distributed-systems/problems/coordination/leader-election/) | Raft, majority quorum, split-brain prevention |
| [Consistent Hashing](distributed-systems/problems/coordination/consistent-hashing/) | Hash ring, virtual nodes, rebalancing |

#### Data Management (5) — Caching, config, session, vector DB, feature store
| Problem | Key Concepts |
|---------|-------------|
| [Distributed Cache](distributed-systems/problems/data-management/distributed-cache/) | Redis Cluster, slot-based partitioning, replication, failover |
| [Distributed Config](distributed-systems/problems/data-management/distributed-config/) | Etcd/Consul, long-polling, local cache, secrets management |
| [Distributed Session](distributed-systems/problems/data-management/distributed-session/) | Redis sessions, JWT, security, scaling |
| [Distributed Vector DB](distributed-systems/problems/data-management/distributed-vector-db/) | HNSW/IVF-PQ, ANN search, sharding, metadata filtering |
| [Feature Store](distributed-systems/problems/data-management/feature-store/) | Online/offline storage, point-in-time correctness, training-serving skew |

#### Messaging & Events (2) — Event sourcing, CQRS
| Problem | Key Concepts |
|---------|-------------|
| [Event Sourcing](distributed-systems/problems/messaging-events/event-sourcing/) | Append-only store, snapshots, projections, schema evolution |
| [CQRS Pattern](distributed-systems/problems/messaging-events/cqs-pattern/) | Command/query separation, read models, eventual consistency |

#### Resilience (2) — Circuit breaker, rate limiting
| Problem | Key Concepts |
|---------|-------------|
| [Circuit Breaker](distributed-systems/problems/resilience/circuit-breaker/) | Three states, failure detection, fallback, distributed state |
| [Distributed Rate Limiter](distributed-systems/problems/resilience/distributed-rate-limiter/) | Token bucket, sliding window, Redis Lua, local cache |

#### Observability (2) — Tracing, metrics
| Problem | Key Concepts |
|---------|-------------|
| [Distributed Tracing](distributed-systems/problems/observability/distributed-tracing/) | OpenTelemetry, sampling, span collection, tiered storage |
| [Distributed Metrics](distributed-systems/problems/observability/distributed-metrics/) | TSDB, cardinality, downsampling, alerting |

#### Infrastructure (4) — ID generation, search, file storage, secret management
| Problem | Key Concepts |
|---------|-------------|
| [Distributed ID Generator](distributed-systems/problems/infrastructure/distributed-id-generator/) | Snowflake, UUID v7, batch pre-allocation, clock handling |
| [Distributed Search](distributed-systems/problems/infrastructure/distributed-search/) | Inverted index, sharding, relevance tuning, autocomplete |
| [Distributed File Storage](distributed-systems/problems/infrastructure/distributed-file-storage/) | Erasure coding, multipart upload, lifecycle, CDN |
| [Distributed Secret Management](distributed-systems/problems/infrastructure/distributed-secret-management/) | AES-256-GCM, Shamir sharing, dynamic secrets, RBAC |

#### Scheduling (2) — Task scheduling, workflow orchestration
| Problem | Key Concepts |
|---------|-------------|
| [Distributed Scheduler](distributed-systems/problems/scheduling/distributed-scheduler/) | Cron, DAG workflows, worker management, exactly-once |
| [Distributed Task Scheduler](distributed-systems/problems/scheduling/distributed-task-scheduler/) | DAG execution, idempotency, leader-based scheduling, retries |

## Java (5 Topics + 73 Problems across 6 Categories)

### Topics
| Topic | Key Concepts |
|-------|-------------|
| [Concurrency](java/concurrency/) | Threads, locks, executors, CompletableFuture, concurrent collections, deadlocks |
| [Collections](java/collections/) | HashMap internals, ConcurrentHashMap, ArrayList vs LinkedList, time complexity |
| [JVM](java/jvm/) | Memory model, GC algorithms (G1/ZGC), JIT compilation, class loading |
| [Streams](java/streams/) | Intermediate/terminal operations, collectors, parallel streams, best practices |
| [Performance](java/performance/) | Profiling (JFR/async-profiler), GC tuning, benchmarking (JMH), I/O optimization |

### Concurrency Problems (25 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Thread Pool](java/problems/thread-pool/) | Worker threads, rejection policies, queue selection |
| [Producer-Consumer](java/problems/producer-consumer/) | BlockingQueue, wait/notify, semaphore |
| [ReadWriteLock](java/problems/readwritelock/) | Shared/exclusive locks, writer starvation, fairness |
| [Fair ReadWriteLock](java/problems/read-write-lock-fair/) | FIFO ordering, writer starvation prevention |
| [Latch & Barrier](java/problems/latch-barrier/) | CountdownLatch, CyclicBarrier, Phaser |
| [Blocking Queue](java/problems/blocking-queue/) | Condition variables, circular array, interruptible |
| [Semaphore](java/problems/semaphore/) | Permits, fair/non-fair, resource pooling |
| [Cache with Expiry](java/problems/cache-expiry/) | TTL, DelayQueue, lazy + eager cleanup |
| [Rate Limiter](java/problems/rate-limiter/) | Token bucket, sliding window, thread safety |
| [Double-Checked Locking](java/problems/double-checked-locking/) | Volatile, instruction reordering, Bill Pugh pattern |
| [Actor Model](java/problems/actor-model/) | Message passing, mailbox, supervision, isolation |
| [Disruptor Pattern](java/problems/disruptor-pattern/) | Lock-free ring buffer, cache line padding |
| [Phaser](java/problems/phaser/) | Dynamic parties, multi-phase, hierarchical phasers |
| [Virtual Threads](java/problems/virtual-threads/) | Project Loom, pinning, migration from reactive |
| [Structured Concurrency](java/problems/structured-concurrency/) | Task scope, fork/join, cancellation |
| [StampedLock](java/problems/stamped-lock/) | Optimistic reads, conversion, non-reentrant |
| [Lock-Free Stack](java/problems/lock-free-stack/) | CAS, ABA problem, memory reclamation |
| [Exchanger](java/problems/exchanger/) | Two-thread swap, buffer swapping |
| [Concurrency Fundamentals](java/problems/concurrency/) | Thread lifecycle, synchronization, volatile, JMM |
| [AtomicReferenceFieldUpdater](java/problems/atomic-reference-field-updater/) | Lock-free field update, CAS, VarHandle |
| [CompletableFuture Advanced](java/problems/completion-advanced/) | Async composition, retry, timeout, fallback |
| [Record Patterns & Switch](java/concurrency/problems/record-patterns-switch/) | Java 16+, record destructuring, switch patterns, guards |
| [Virtual Threads Deep Dive](java/concurrency/problems/virtual-threads-deep-dive/) | Java 21, Project Loom, pinning, migration from reactive |
| [Pattern Matching](java/concurrency/problems/pattern-matching/) | Java 16+, instanceof patterns, scope rules, migration |

### Collections Problems (8 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [HashMap Internals](java/collections/problems/hashmap-internals/) | Bucket array, hash mixing, treeification |
| [ConcurrentHashMap](java/collections/problems/concurrent-hashmap/) | CAS + synchronized, weakly consistent iterators |
| [LRU Cache](java/collections/problems/lru-cache-linkedhashmap/) | Access order, removeEldestEntry, Caffeine |
| [TreeMap & Red-Black Tree](java/collections/problems/treemap-redblack/) | Self-balancing BST, rotations |
| [Priority Queue](java/collections/problems/priority-heap/) | Heapify, offer/poll, top-K |
| [CopyOnWriteArrayList](java/collections/problems/copyonwritearraylist/) | Copy-on-write, snapshot iterator |
| [Blocking Queue Design](java/collections/problems/blocking-queue-design/) | Two-lock design, condition variables |
| [Custom Collection](java/collections/problems/custom-collection/) | Decorator pattern, iterator |

### JVM Problems (8 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Memory Leak Detection](java/jvm/problems/memory-leak-detection/) | Heap dumps, MAT, GC root tracing |
| [GC Tuning](java/jvm/problems/gc-tuning-strategies/) | G1/ZGC selection, pause time target |
| [Custom ClassLoader](java/jvm/problems/custom-classloader/) | Delegation model, hot reloading |
| [JIT Optimization](java/jvm/problems/jit-optimization/) | Inlining, escape analysis, tiered compilation |
| [Thread Dump Analysis](java/jvm/problems/thread-dump-analysis/) | Thread states, deadlock detection |
| [Heap Dump Analysis](java/jvm/problems/heap-dump-analysis/) | MAT analysis, dominator tree |
| [OOM Prevention](java/jvm/problems/oom-prevention/) | Heap sizing, monitoring, graceful degradation |
| [JVM Startup Optimization](java/jvm/problems/jvm-startup-optimization/) | AppCDS, lazy init, GraalVM Native Image |

### Performance Problems (8 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Connection Pool](java/performance/problems/connection-pool/) | Borrow/return, validation, HikariCP |
| [Object Pool](java/performance/problems/object-pool/) | ThreadLocal pooling, state reset |
| [Caffeine Cache](java/performance/problems/caffeine-cache/) | Window TinyLFU, async loading |
| [JMH Benchmark](java/performance/problems/jmh-benchmark/) | Warm-up, Blackhole, forks |
| [Async I/O Server](java/performance/problems/async-io-server/) | Netty event loop, zero-copy |
| [Batch Processing](java/performance/problems/batch-processor/) | Chunk processing, checkpointing |
| [String Optimization](java/performance/problems/string-optimization/) | StringBuilder, interning |
| [Memory Profiler](java/performance/problems/memory-profiler/) | JFR allocation tracking, sampling |

### Streams Problems (6 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Custom Collector](java/streams/problems/custom-collector/) | Supplier, accumulator, combiner |
| [Pipeline Optimization](java/streams/problems/stream-pipeline-optimization/) | Lazy evaluation, short-circuiting |
| [Parallel Stream Tuning](java/streams/problems/parallel-stream-tuning/) | ForkJoinPool, work stealing |
| [Stream vs Loop](java/streams/problems/stream-vs-loop/) | JMH comparison, primitive streams |
| [Data Aggregation](java/streams/problems/data-aggregation/) | groupingBy, downstream collectors |
| [Reactive Stream](java/streams/problems/reactive-stream/) | Backpressure, Publisher/Subscriber |

### Concurrency Design Problems (6 Problems)
| Problem | Key Concepts |
|---------|-------------|
| [Deadlock Detector](java/concurrency/problems/deadlock-detector/) | Wait-for graph, DFS cycle detection |
| [Thread-Safe Singleton](java/concurrency/problems/thread-safe-singleton/) | Bill Pugh, enum, double-checked locking |
| [Event Loop](java/concurrency/problems/event-loop/) | Selector, task queue, non-blocking I/O |
| [Work Stealing Pool](java/concurrency/problems/work-stealing-pool/) | Per-thread deque, CAS, fork/join |
| [Read-Write Cache](java/concurrency/problems/read-write-cache/) | StampedLock, optimistic reads |
| [Async Pipeline](java/concurrency/problems/async-pipeline/) | Stage chaining, backpressure |

## Notes

- [Interview Questions](notes/interview-questions.md) — **80 staff-level questions** across HLD, LLD, Java, and Distributed Systems
- [Trade-offs](notes/trade-offs.md) — SQL vs NoSQL, consistency vs availability, build vs buy, with staff-level framework
- [Revision Checklist](notes/revision-checklist.md) — Complete checklist with interview frameworks and weekly revision plan

## Trade-offs (25 Architectural Trade-offs)

Architectural trade-offs with decision frameworks and real-world examples. See [Trade-offs Module](tradeoffs/) for details.

| Category | Trade-off | Description |
|----------|-----------|-------------|
| **Data Storage** | [SQL vs NoSQL](tradeoffs/sql-vs-nosql/) | Relational vs non-relational databases |
| **Data Storage** | [Consistency vs Availability](tradeoffs/consistency-vs-availability/) | CAP theorem trade-offs in practice |
| **Data Storage** | [Normalization vs Denormalization](tradeoffs/normalization-vs-denormalization/) | Data redundancy vs query performance |
| **Data Storage** | [Row-store vs Column-store](tradeoffs/row-store-vs-column-store/) | OLTP vs OLAP storage engines |
| **Architecture** | [Monolith vs Microservices](tradeoffs/monolith-vs-microservices/) | Single deployment vs distributed services |
| **Architecture** | [Sync vs Async Communication](tradeoffs/sync-vs-async/) | REST/gRPC vs message queues |
| **Architecture** | [Push vs Pull](tradeoffs/push-vs-pull/) | Server-push vs client-pull data delivery |
| **Architecture** | [REST vs gRPC](tradeoffs/rest-vs-grpc/) | JSON/HTTP vs Protobuf/HTTP2 |
| **Architecture** | [GraphQL vs REST](tradeoffs/graphql-vs-rest/) | Client-specified vs fixed endpoints |
| **Architecture** | [Event-Driven vs Request-Response](tradeoffs/event-driven-vs-request-response/) | Async events vs sync requests |
| **Architecture** | [Serverless vs Containers](tradeoffs/serverless-vs-containers/) | Lambda functions vs Docker/Kubernetes |
| **Scalability** | [Horizontal vs Vertical Scaling](tradeoffs/horizontal-vs-vertical/) | Add more machines vs bigger machines |
| **Scalability** | [Sharding vs Replication](tradeoffs/sharding-vs-replication/) | Data partitioning vs data copying |
| **Scalability** | [CDN vs Origin Server](tradeoffs/cdn-vs-origin/) | Edge caching vs centralized storage |
| **Scalability** | [Connection Pooling](tradeoffs/connection-pooling/) | Reuse connections vs create on demand |
| **Performance** | [Caching Strategies](tradeoffs/caching-strategies/) | Write-through vs write-back vs cache-aside |
| **Performance** | [Batch vs Stream Processing](tradeoffs/batch-vs-stream/) | Offline batch vs real-time stream processing |
| **Performance** | [Compression vs CPU](tradeoffs/compression-vs-cpu/) | Reduce bandwidth vs increase compute |
| **Performance** | [Lazy vs Eager Loading](tradeoffs/lazy-vs-eager/) | Load on demand vs load upfront |
| **DevOps** | [CI/CD Pipeline](tradeoffs/ci-cd-pipeline/) | Self-hosted vs managed CI/CD, deployment strategies |
| **DevOps** | [Observability Strategies](tradeoffs/observability-strategies/) | Metrics vs logs vs traces, correlation, cost management |
| **AI/ML** | [Vector DB vs Traditional DB](tradeoffs/vector-db-vs-traditional/) | ANN search vs relational queries, semantic vs exact match |
| **AI/ML** | [Build vs Buy AI Infrastructure](tradeoffs/build-vs-buy-ai/) | Self-hosted models vs managed AI services, cost vs control |
| **Architecture** | [Edge Computing vs Centralized](tradeoffs/edge-vs-centralized/) | Process at edge vs cloud, latency vs scalability |

## Diagrams

HLD diagrams are created using [Excalidraw](https://excalidraw.com). Install the **Excalidraw Integration** plugin in IntelliJ IDEA to view and edit `.excalidraw` files.

See [hld/diagrams/README.md](hld/diagrams/README.md) for details.

## References

Problem statements and interview questions are inspired by:
- [AlgoMaster](https://algomaster.io/) — System design interview platform
- [HelloInterview](https://www.hellointerview.com/) — AI-powered interview prep
- [ByteByteGo](https://bytebytego.com/) — System design illustrated
- [LLD Coding](https://www.lldcoding.com/) — Low-level design practice
- [Educative](https://www.educative.io/) — Grokking the system design interview

## API Modeling (10 Problems + Tests)

Comprehensive API design patterns including REST, gRPC, GraphQL, versioning, security, pagination, and error handling. See [API Modeling Module](api-modeling/) for details.

| Problem | Key Concepts |
|---------|-------------|
| [REST API Design](api-modeling/problems/rest-api-design/) | Resource modeling, HTTP methods, status codes, HATEOAS, pagination |
| [gRPC API Design](api-modeling/problems/grpc-api-design/) | Protobuf, streaming, code generation, interceptors |
| [GraphQL API Design](api-modeling/problems/graphql-api-design/) | Schema design, resolvers, DataLoader, subscriptions |
| [API Versioning](api-modeling/problems/api-versioning/) | URI vs header versioning, deprecation strategy, backward compatibility |
| [API Gateway](api-modeling/problems/api-gateway/) | Routing, aggregation, rate limiting, authentication, circuit breaking |
| [Webhook Design](api-modeling/problems/webhook-design/) | Event delivery, retry logic, signature verification, idempotency |
| [OpenAPI Specification](api-modeling/problems/openapi-spec/) | Contract-first design, code generation, documentation |
| [API Security](api-modeling/problems/api-security/) | OAuth 2.0, JWT, API keys, CORS, CSRF protection |
| [API Pagination](api-modeling/problems/api-pagination/) | Offset, cursor, keyset pagination, performance |
| [API Error Handling](api-modeling/problems/api-error-handling/) | Error codes, retryable errors, Problem Detail RFC 7807 |

## Blogs & Articles (25 Technical Articles)

Curated technical articles for staff engineers across 5 categories. See [Blogs & Articles](blogs-articles/) for details.

- **System Design** (5 articles): URL Shortener, News Feed, Chat System, Microservices Patterns, CAP Theorem
- **Distributed Systems** (5 articles): Consistent Hashing, Raft, Gossip Protocol, Distributed Tracing, Event Sourcing
- **Java Concurrency** (5 articles): JVM Memory Model, Virtual Threads, CompletableFuture, Concurrent Collections, Lock-Free
- **DevOps & SRE** (5 articles): SRE Principles, Kubernetes, CI/CD, Observability, Incident Management
- **Career Growth** (5 articles): Staff Engineer Handbook, Technical Leadership, System Design Interviews, Code Review, Mentoring

## Recommended Books (10 Essential Books)

Curated book list with summaries and key takeaways. See [Recommended Books](recommended-books/) for details.

- **System Design**: Designing Data-Intensive Applications, System Design Interview (Vol 1 & 2), Building Microservices
- **Java**: Effective Java, Java Concurrency in Practice, Clean Code
- **Distributed Systems**: Distributed Systems for Fun and Profit, Site Reliability Engineering
- **Career**: The Staff Engineer's Path, Accelerate

## How to Use

1. **Start with fundamentals**: Read HLD and LLD fundamentals first
2. **Study case studies**: Go through each HLD case study (README → Architecture → API → Database)
3. **Practice LLD problems**: Implement each LLD problem with proper design patterns (start with easy, progress to hard)
4. **Master concurrency**: Solve LLD and Java concurrency problems to understand thread-safe design
5. **Design databases**: Work through db-design problems — relational, NoSQL, hybrid, and advanced topics
6. **Design APIs**: Practice API modeling problems — REST, gRPC, GraphQL, security, and testing
7. **Review distributed systems**: Understand Kafka, Redis, consistency models, and 20 problems across 7 categories (coordination, data management, messaging, resilience, observability, infrastructure, scheduling)
8. **Master Java**: 73 problems across 6 categories — concurrency (25), collections (8), JVM (8), performance (8), streams (6), and concurrency design (6)
9. **Study trade-offs**: Understand 25 architectural decisions and their implications
10. **Read blogs & articles**: Deep-dive into technical topics across 5 categories
11. **Read recommended books**: Start with "must read" books for staff-level knowledge
12. **Use the revision checklist**: Track progress and follow the weekly revision plan
13. **Mock interviews**: Practice with the 80 interview questions under timed conditions
