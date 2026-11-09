# Revision Checklist

## HLD Fundamentals
- [ ] Scalability (vertical vs horizontal, metrics, strategies)
- [ ] Load balancing (L4 vs L7, algorithms, health checks, global LB)
- [ ] Caching (multi-tier, strategies, invalidation, stampede protection)
- [ ] Database sharding (strategies, shard key selection, rebalancing)
- [ ] Replication (topologies, sync vs async, failover, replication lag)
- [ ] CAP theorem and consistency models (strong, eventual, session, causal)
- [ ] Message queue patterns (pub/sub, point-to-point, delivery semantics)
- [ ] Rate limiting (algorithms, distributed implementation, response handling)

## LLD Fundamentals
- [ ] SOLID principles (SRP, OCP, LSP, ISP, DIP with examples)
- [ ] Design patterns (Strategy, Observer, Factory, Builder, Decorator, State, Command)
- [ ] OOP concepts (encapsulation, abstraction, inheritance, polymorphism, composition)
- [ ] UML diagrams (class, sequence, state machine, component)

## HLD Case Studies
- [ ] URL Shortener (short code generation, redirect optimization, analytics)
- [ ] WhatsApp (MQTT, Signal Protocol, presence, offline delivery)
- [ ] Instagram (feed strategy, media processing, caching, recommendations)
- [ ] Uber (geospatial indexing, matching algorithm, surge pricing, real-time tracking)
- [ ] YouTube (transcoding pipeline, adaptive bitrate, CDN, recommendations)
- [ ] Notification System (multi-channel, templating, rate limiting, delivery tracking)
- [ ] E-commerce System (catalog, cart, checkout, inventory, payment, search)
- [ ] Payment System (idempotency, outbox pattern, fraud detection, PCI-DSS)

## LLD Practice Problems
- [ ] Parking Lot (slot assignment, dynamic pricing, concurrency control)
- [ ] Elevator System (dispatch algorithm, state machine, peak-hour handling)
- [ ] Library Management (catalog, borrowing, reservations, fines)
- [ ] Snake and Ladder (board as graph, game state, real-time sync)
- [ ] Tic-Tac-Toe (minimax algorithm, server-authoritative design)
- [ ] Chess (bitboard representation, move validation, special moves)
- [ ] Splitwise (debt optimization, decimal precision, multi-currency)
- [ ] Vending Machine (state machine, change dispensing, payment processing)
- [ ] Movie Ticket Booking (seat reservation, double-booking prevention, concurrency)
- [ ] Notification Service (multi-channel, preferences, templating, analytics)

## Distributed Systems
- [ ] Kafka architecture (topics, partitions, producers, consumers, replication)
- [ ] Redis data structures and use cases (caching, rate limiting, pub/sub, streams)
- [ ] ZooKeeper coordination (ZNodes, watches, leader election, distributed locks)
- [ ] Consistency models (strong, eventual, session, causal, quorum-based)
- [ ] Distributed locks (Redis SETNX, Redlock, ZooKeeper, database-based)
- [ ] Idempotency (idempotency keys, database constraints, message deduplication)
- [ ] Saga pattern (choreography vs orchestration, compensating transactions)
- [ ] Outbox pattern (reliable event publishing, polling vs CDC, idempotent consumers)

## Java
- [ ] Concurrency (threads, locks, executors, CompletableFuture, concurrent collections)
- [ ] Collections (HashMap internals, ConcurrentHashMap, ArrayList vs LinkedList)
- [ ] JVM (memory model, GC algorithms, JIT compilation, class loading)
- [ ] Streams API (intermediate/terminal operations, collectors, parallel streams)
- [ ] Performance tuning (profiling tools, GC tuning, benchmarking with JMH)

## Staff-Level Interview Prep

### System Design Interview Framework
1. **Clarify requirements**: Functional, non-functional, scale, constraints
2. **Estimate scale**: Users, RPS, storage, bandwidth, database size
3. **High-level design**: Components, data flow, technology choices
4. **Deep dive**: Database schema, API design, caching, scaling
5. **Identify bottlenecks**: Single points of failure, scaling limits
6. **Discuss trade-offs**: Consistency vs availability, latency vs throughput
7. **Staff-level additions**: Observability, cost optimization, failure scenarios, migration strategy

### LLD Interview Framework
1. **Clarify requirements**: Functional, non-functional, edge cases
2. **Identify entities**: Core classes, relationships, attributes
3. **Design class diagram**: Classes, interfaces, relationships
4. **Implement key methods**: Core logic with proper design patterns
5. **Discuss extensibility**: How to add new features without modifying existing code
6. **Staff-level additions**: Thread safety, error handling, testing strategy, performance considerations

### Common Staff-Level Questions
- How would you handle a 10x traffic spike?
- How do you ensure zero-downtime deployments?
- How do you debug a production issue with high p99 latency?
- How do you design for multi-region deployment?
- How do you handle data migration with zero downtime?
- How do you implement feature flags for gradual rollout?
- How do you design an observability strategy (metrics, logs, traces)?
- How do you optimize cloud costs for a high-traffic service?
- How do you handle schema migrations in a distributed system?
- How do you design for disaster recovery (RTO, RPO)?

## Weekly Revision Plan

| Day | Focus Area | Time |
|-----|-----------|------|
| Monday | HLD Fundamentals + 1 Case Study | 2 hours |
| Tuesday | LLD Fundamentals + 1 Problem | 2 hours |
| Wednesday | Distributed Systems + Java | 2 hours |
| Thursday | HLD Case Study (mock interview) | 2 hours |
| Friday | LLD Problem (mock interview) | 2 hours |
| Saturday | Full system design (timed, 45 min) | 1 hour |
| Sunday | Review weak areas + trade-offs | 1 hour |
