# Interview Questions

## System Design (HLD) - Staff Level

### Core Systems
1. Design a URL shortener (bit.ly) — **covered in case studies**
2. Design a social media feed (Instagram/Twitter) — **covered in case studies**
3. Design a ride-sharing app (Uber) — **covered in case studies**
4. Design a video streaming service (YouTube/Netflix) — **covered in case studies**
5. Design a chat application (WhatsApp) — **covered in case studies**
6. Design an e-commerce platform (Amazon) — **covered in case studies**
7. Design a payment processing system (Stripe) — **covered in case studies**
8. Design a notification system (multi-channel) — **covered in case studies**

### Advanced Systems
9. Design a web crawler (Google) — handle scale, politeness, deduplication, indexing
10. Design a rate limiter (distributed) — token bucket, sliding window, consistent hashing
11. Design a distributed cache (Redis at scale) — caching strategies, invalidation, consistency
12. Design a key-value store (DynamoDB) — consistent hashing, replication, conflict resolution
13. Design a search engine (Google/Elasticsearch) — indexing, ranking, distributed search
14. Design a CDN (CloudFront) — edge caching, origin shield, geo-routing
15. Design a log aggregation system (Splunk/Datadog) — collection, indexing, querying
16. Design a recommendation system (Netflix/Amazon) — collaborative filtering, content-based, ML
17. Design a stock trading system — order matching, real-time pricing, audit trail
18. Design a food delivery app (DoorDash/UberEats) — order tracking, driver matching, ETA
19. Design a live streaming platform (Twitch) — RTMP ingest, HLS output, chat, low latency
20. Design a blockchain system — consensus, blocks, transactions, mining

## Low-Level Design (LLD) - Staff Level

### Core Problems (Covered)
1. Design a parking lot — **covered in problems**
2. Design an elevator system — **covered in problems**
3. Design a library management system — **covered in problems**
4. Design a chess game — **covered in problems**
5. Design a tic-tac-toe game — **covered in problems**
6. Design a vending machine — **covered in problems**
7. Design a movie ticket booking system — **covered in problems**
8. Design a splitwise app — **covered in problems**
9. Design a snake and ladder game — **covered in problems**
10. Design a notification service — **covered in problems**

### Additional Problems
11. Design a deck of cards — card representation, shuffling, dealing, game rules
12. Design a car rental system — vehicle types, booking, pricing, returns
13. Design an online auction system (eBay) — bidding, timers, winner determination
14. Design a food ordering system — menu, cart, order tracking, delivery
15. Design a hotel booking system — rooms, availability, pricing, check-in/out
16. Design a flight booking system — seats, routes, pricing, boarding
17. Design a delivery tracking system — packages, couriers, real-time location
18. Design a social network graph — friends, feed, suggestions, communities
19. Design a task scheduler (Cron) — scheduling, execution, retry, monitoring
20. Design a config management system — versioning, validation, distribution

## Java - Staff Level

### Core
1. Explain the difference between HashMap and ConcurrentHashMap
2. How does String interning work?
3. Explain the Java memory model (heap, stack, metaspace, direct memory)
4. What is the difference between synchronized and ReentrantLock?
5. How does G1 GC work? When to use ZGC?
6. Explain the producer-consumer problem and solutions
7. What are the different types of references in Java (Strong, Weak, Soft, Phantom)?
8. How does CompletableFuture work? Chain operations and error handling

### Advanced
9. Explain Java's happens-before relationship and memory visibility
10. How does the JIT compiler optimize code? (Inlining, escape analysis, lock elimination)
11. What is the difference between fail-fast and fail-safe iterators?
12. How does ConcurrentHashMap achieve thread safety without global locking?
13. Explain the double-checked locking idiom and why volatile is needed
14. What are the different GC algorithms and when to use each?
15. How does Java's class loading mechanism work? (Delegation model, custom classloaders)
16. Explain the difference between process, thread, and fiber (virtual threads)
17. How does Java's module system (JPMS) work? (Java 9+)
18. What are records and sealed classes? (Java 14+/17+)
19. How does Java's pattern matching work? (Java 16+/21+)
20. Explain virtual threads (Project Loom) and structured concurrency (Java 21+)

## Distributed Systems - Staff Level

### Core
1. Explain CAP theorem with real-world examples
2. What is the difference between Kafka and RabbitMQ?
3. How does consistent hashing work? Why virtual nodes?
4. Explain the two-phase commit protocol and its limitations
5. What is a distributed lock and how to implement it? (Redis, ZooKeeper)
6. How does Raft consensus algorithm work?
7. What is idempotency and why is it important in distributed systems?
8. Explain the outbox pattern and how it ensures reliable event publishing

### Advanced
9. Explain the difference between strong, eventual, and causal consistency
10. How does the Saga pattern work? Choreography vs Orchestration
11. What is the difference between horizontal and vertical scaling?
12. How does database sharding work? Shard key selection strategies
13. Explain the difference between synchronous and asynchronous replication
14. What is a circuit breaker pattern? How does it prevent cascade failures?
15. How does leader election work in distributed systems? (Raft, ZooKeeper)
16. What is the difference between microservices and monolith? When to choose each?
17. Explain the CQRS pattern and when to use it
18. What is event sourcing? How does it differ from traditional CRUD?
19. How does a service mesh work? (Istio, Linkerd)
20. Explain the difference between gRPC and REST. When to use each?
