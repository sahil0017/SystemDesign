# Distributed Systems

Comprehensive module covering distributed systems concepts, tools, and patterns essential for staff-level engineering. Covers message queues, caching, coordination, consistency models, and distributed patterns.

**References**: [Educative.io](https://www.educative.io/), [ByteByteGo](https://bytebytego.com/), [HelloInterview](https://www.hellointerview.com/)

## Topics (8)

Conceptual guides for understanding core distributed systems building blocks.

| Topic | Key Concepts |
|-------|-------------|
| [Kafka](problems/kafka/) | Topics, partitions, producers/consumers, delivery semantics, consumer groups |
| [Redis](problems/redis/) | Data structures, persistence, clustering, pub/sub, Lua scripting, Streams |
| [ZooKeeper](problems/zookeeper/) | ZNodes, watches, ensemble, leader election, distributed locks |
| [Consistency Models](problems/consistency-models/) | Strong, eventual, session, causal, CAP theorem, quorum-based |
| [Distributed Locks](problems/distributed-locks/) | Redis SETNX/Redlock, ZooKeeper, database-based, TTL, atomic release |
| [Idempotency](problems/idempotency/) | Idempotency keys, database constraints, message deduplication, TTL |
| [Saga Pattern](problems/saga-pattern/) | Choreography vs orchestration, compensating transactions, event sourcing |
| [Outbox Pattern](problems/outbox-pattern/) | Reliable event publishing, polling vs CDC (Debezium), idempotent consumers |

## Problems (17 across 7 categories)

Practice problems organized by problem type so you can study related patterns together.

### Coordination (3)
Core mechanisms for nodes to agree on shared state and safely access resources.

| Problem | Key Concepts |
|---------|-------------|
| [Distributed Lock](problems/coordination/distributed-lock/) | RedLock algorithm, TTL, clock drift, watchdog |
| [Leader Election](problems/coordination/leader-election/) | Raft, majority quorum, split-brain prevention |
| [Consistent Hashing](problems/coordination/consistent-hashing/) | Hash ring, virtual nodes, rebalancing |

### Data Management (3)
Systems for storing, caching, and managing state across nodes.

| Problem | Key Concepts |
|---------|-------------|
| [Distributed Cache](problems/data-management/distributed-cache/) | Redis Cluster, slot-based partitioning, replication, failover |
| [Distributed Config](problems/data-management/distributed-config/) | Etcd/Consul, long-polling, local cache, secrets management |
| [Distributed Session](problems/data-management/distributed-session/) | Redis sessions, JWT, security, scaling |

### Messaging & Events (2)
Event-driven patterns for reliable delivery and state reconstruction.

| Problem | Key Concepts |
|---------|-------------|
| [Event Sourcing](problems/messaging-events/event-sourcing/) | Append-only store, snapshots, projections, schema evolution |
| [CQRS Pattern](problems/messaging-events/cqs-pattern/) | Command/query separation, read models, eventual consistency |

### Resilience (2)
Patterns for protecting services from cascading failures and enforcing quotas.

| Problem | Key Concepts |
|---------|-------------|
| [Circuit Breaker](problems/resilience/circuit-breaker/) | Three states, failure detection, fallback, distributed state |
| [Distributed Rate Limiter](problems/resilience/distributed-rate-limiter/) | Token bucket, sliding window, Redis Lua, local cache |

### Observability (2)
Systems for monitoring, tracing, and debugging distributed microservices.

| Problem | Key Concepts |
|---------|-------------|
| [Distributed Tracing](problems/observability/distributed-tracing/) | OpenTelemetry, sampling, span collection, tiered storage |
| [Distributed Metrics](problems/observability/distributed-metrics/) | TSDB, cardinality, downsampling, alerting |

### Infrastructure (3)
Platform-level services: ID generation, search, and object storage at scale.

| Problem | Key Concepts |
|---------|-------------|
| [Distributed ID Generator](problems/infrastructure/distributed-id-generator/) | Snowflake, UUID v7, batch pre-allocation, clock handling |
| [Distributed Search](problems/infrastructure/distributed-search/) | Inverted index, sharding, relevance tuning, autocomplete |
| [Distributed File Storage](problems/infrastructure/distributed-file-storage/) | Erasure coding, multipart upload, lifecycle, CDN |

### Scheduling (2)
Distributed task execution and workflow orchestration.

| Problem | Key Concepts |
|---------|-------------|
| [Distributed Scheduler](problems/scheduling/distributed-scheduler/) | Cron, DAG workflows, worker management, exactly-once |
| [Distributed Task Scheduler](problems/scheduling/distributed-task-scheduler/) | DAG execution, idempotency, leader-based scheduling, retries |

## How to Use

1. **Start with topics**: Read each topic to understand the underlying concepts
2. **Pick a problem category**: Choose the category that matches the system you want to understand
3. **Practice problems**: Implement each problem to apply the concepts
4. **Cross-reference**: Relate topics to HLD case studies and trade-offs
