# Low-Level Design (LLD)

This section covers low-level design concepts, design patterns, and practical problem-solving.

**References**: [AlgoMaster](https://algomaster.io/learn/lld), [Educative.io](https://www.educative.io/courses/grokking-the-low-level-design-interview-using-ood-principles), [HelloInterview](https://www.hellointerview.com/learn/low-level-design), [LLD Coding](https://www.lldcoding.com/)

## Contents

- [Fundamentals](fundamentals/) - Core LLD concepts
- [Problems](problems/) - Practice problems organized by difficulty and category
- [Common Utilities](common/) - Reusable code utilities

## Fundamentals

- [SOLID Principles](fundamentals/solid-principles/) - Five design principles
- [Design Patterns](fundamentals/design-patterns/) - Creational, structural, behavioral patterns
- [OOP](fundamentals/oop/) - Object-oriented programming concepts
- [UML](fundamentals/uml/) - Unified Modeling Language

## Problems

Problems are organized by difficulty level and a dedicated concurrency category.

### Easy (6 Problems)

| Problem | Key Concepts | Reference |
|---------|-------------|-----------|
| [Parking Lot](problems/easy/parking-lot/) | Multi-level slots, dynamic pricing, vehicle types | AlgoMaster, HelloInterview |
| [LRU Cache](problems/easy/lru-cache/) | HashMap + Doubly Linked List, O(1) operations | AlgoMaster, LLD Coding |
| [Snake and Ladder](problems/easy/snake-and-ladder/) | Board game simulation, state management | AlgoMaster |
| [Task Management](problems/easy/task-management-system/) | State machine, search indexing, optimistic locking | AlgoMaster, LLD Coding |
| [Tic-Tac-Toe](problems/easy/tic-tac-toe/) | Game engine, win detection, state management | AlgoMaster |
| [Vending Machine](problems/easy/vending-machine/) | State pattern, coin handling, product inventory | AlgoMaster |

### Medium (15 Problems)

| Problem | Key Concepts | Reference |
|---------|-------------|-----------|
| [Stack Overflow](problems/medium/stack-overflow/) | Voting, reputation system, Elasticsearch | AlgoMaster, LLD Coding |
| [ATM](problems/medium/atm/) | State machine, strategy pattern, PIN security | AlgoMaster, LLD Coding |
| [Logging Framework](problems/medium/logging-framework/) | Chain of responsibility, async logging | AlgoMaster, LLD Coding |
| [Pub/Sub System](problems/medium/pub-sub-system/) | Observer pattern, backpressure, delivery guarantees | AlgoMaster, LLD Coding |
| [Car Rental](problems/medium/car-rental-system/) | Double-booking prevention, dynamic pricing | AlgoMaster, LLD Coding |
| [Hotel Management](problems/medium/hotel-management-system/) | Interval tree, room state, overbooking prevention | AlgoMaster, LLD Coding |
| [Digital Wallet](problems/medium/digital-wallet/) | Double-entry bookkeeping, idempotency | AlgoMaster, LLD Coding |
| [Airline Management](problems/medium/airline-management-system/) | Seat map, controlled overbooking, fare classes | AlgoMaster, LLD Coding |
| [Traffic Signal](problems/medium/traffic-signal/) | State machine, emergency preemption | AlgoMaster, LLD Coding |
| [Concert Booking](problems/medium/concert-ticket-booking/) | Virtual queue, seat locking, bot prevention | AlgoMaster, LLD Coding |
| [Social Network](problems/medium/social-network/) | Feed fan-out, graph storage, notifications | AlgoMaster, LLD Coding |
| [Elevator System](problems/medium/elevator-system/) | Scheduling algorithms, request optimization | AlgoMaster |
| [Library Management](problems/medium/library-management/) | Book catalog, borrowing, reservation system | AlgoMaster |
| [Splitwise](problems/medium/splitwise/) | Expense splitting, debt simplification, graph algorithms | AlgoMaster |
| [Notification Service](problems/medium/notification-service/) | Multi-channel delivery, templating, rate limiting | AlgoMaster |

### Hard (13 Problems)

| Problem | Key Concepts | Reference |
|---------|-------------|-----------|
| [Spotify](problems/hard/spotify/) | Streaming, recommendations, playlist denormalization | AlgoMaster |
| [Amazon](problems/hard/amazon/) | Microservices, inventory, CQRS, search | AlgoMaster |
| [LinkedIn](problems/hard/linkedin/) | Graph queries, bidirectional BFS, feed personalization | AlgoMaster |
| [CricInfo](problems/hard/cricinfo/) | Event sourcing, WebSocket, real-time stats | AlgoMaster |
| [Chess](problems/hard/chess/) | Game engine, move validation, piece movement patterns | AlgoMaster |
| [Coffee Vending](problems/hard/coffee-vending-machine/) | State pattern, recipe extensibility, ingredient management | AlgoMaster |
| [Restaurant](problems/hard/restaurant-management/) | Kitchen workflow, bill splitting, priority queue | AlgoMaster |
| [Stock Exchange](problems/hard/stock-exchange/) | Matching engine, order book, lock-free structures | AlgoMaster |
| [Course Registration](problems/hard/course-registration/) | DAG prerequisites, interval tree, registration queue | AlgoMaster |
| [Movie Ticket Booking](problems/hard/movie-ticket-booking/) | Seat selection, show management, payment | AlgoMaster |
| [Online Auction](problems/hard/online-auction/) | Proxy bidding, time-wheel, soft close | AlgoMaster |
| [Food Delivery](problems/hard/food-delivery/) | GeoHash/H3, real-time tracking, ETA estimation | AlgoMaster |
| [Ride-Sharing](problems/hard/ride-sharing/) | H3 indexing, surge pricing, WebSocket tracking | AlgoMaster |

### Concurrency (15 Problems)

Thread-safe systems requiring concurrent access, synchronization, and coordination. See [Concurrency Problems](problems/concurrency/) for details.

| Problem | Key Concurrency Concepts | Reference |
|---------|--------------------------|-----------|
| [Bank Transaction](problems/concurrency/bank-transaction/) | Lock ordering, ReadWriteLock, deadlock prevention | LLD Coding |
| [Train Deadlock](problems/concurrency/train-deadlock/) | Lock ordering, try-lock, rollback, semaphore | LLD Coding |
| [Traffic Light](problems/concurrency/traffic-light/) | State pattern, ScheduledExecutorService, volatile | LLD Coding |
| [Call Center Queue](problems/concurrency/call-center-queue/) | PriorityBlockingQueue, DelayQueue, LongAdder | LLD Coding |
| [Online Matchmaking](problems/concurrency/online-matchmaking/) | ConcurrentHashMap, CAS, atomic state transition | LLD Coding |
| [Multiplayer Game Sync](problems/concurrency/multiplayer-game-sync/) | Copy-on-write, ConcurrentLinkedQueue, CyclicBarrier | LLD Coding |
| [Thread-Safe Cache with TTL](problems/concurrency/thread-safe-cache/) | ConcurrentHashMap, DelayQueue, lazy + eager expiration | AlgoMaster |
| [Concurrent HashMap](problems/concurrency/concurrent-hashmap/) | Segment locking, CAS, striped counters, tree bins | AlgoMaster |
| [Thread-Safe Blocking Queue](problems/concurrency/thread-safe-blocking-queue/) | Condition variables, spurious wakeups, ReentrantLock | AlgoMaster |
| [Concurrent Bloom Filter](problems/concurrency/concurrent-bloom-filter/) | AtomicLongArray, double hashing, lock-free reads | AlgoMaster |
| [Thread Pool](problems/concurrency/thread-pool/) | BlockingQueue, rejection policies, graceful shutdown | LLD Coding |
| [Delivery Truck Loading](problems/concurrency/delivery-truck-loading/) | Fine-grained locking, CAS, bin packing | LLD Coding |
| [Rocket Launch Countdown](problems/concurrency/rocket-launch-countdown/) | CountDownLatch, CyclicBarrier, CompletableFuture | LLD Coding |
| [Jigsaw Puzzle Builder](problems/concurrency/jigsaw-puzzle-builder/) | Per-cell locking, CAS, CountDownLatch | LLD Coding |
| [Warehouse Packing](problems/concurrency/warehouse-packing/) | Per-box locking, CAS, 3D bin packing | LLD Coding |
