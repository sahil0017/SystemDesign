# Trade-offs

## System Design Trade-offs

### SQL vs NoSQL

| Aspect | SQL (PostgreSQL, MySQL) | NoSQL (Cassandra, MongoDB) |
|--------|------------------------|---------------------------|
| **Consistency** | ACID transactions | Eventual consistency (tunable) |
| **Schema** | Fixed schema; migrations | Flexible schema; evolve freely |
| **Queries** | Complex joins; aggregations | Simple queries; denormalized |
| **Scaling** | Vertical; read replicas | Horizontal; automatic sharding |
| **Use case** | Transactions, complex queries | High write throughput, flexible data |
| **Staff insight**: Use **polyglot persistence** — SQL for transactions, NoSQL for reads, time-series for metrics. Don't force one database to do everything.

### Consistency vs Availability (CAP)

| Model | When to Use | Examples |
|-------|-------------|----------|
| **Strong consistency** | Financial transactions, inventory, seat booking | PostgreSQL, Spanner, ZooKeeper |
| **Eventual consistency** | Social feeds, comments, likes, DNS | Cassandra, DynamoDB, CDN |
| **Session consistency** | User profiles, e-commerce carts | Read-your-writes + monotonic reads |
| **Staff insight**: Most systems use **eventual consistency** with **session consistency** for user-facing data. Strong consistency is expensive — use only where required.

### Latency vs Throughput

| Priority | Techniques | Trade-off |
|----------|-----------|-----------|
| **Low latency** | Caching, CDN, async processing, connection pooling | Higher resource usage; possible stale data |
| **High throughput** | Batching, pipelining, parallelism, compression | Higher latency per request; complex error handling |
| **Staff insight**: Optimize for **p99 latency**, not average. Use **async processing** to hide latency from users.

### Build vs Buy

| Factor | Build | Buy |
|--------|-------|-----|
| **Customization** | Full control | Limited to vendor features |
| **Time-to-market** | Slow (months) | Fast (days) |
| **Maintenance** | Your responsibility | Vendor handles |
| **Cost** | High engineering cost | Subscription/usage fees |
| **Vendor lock-in** | None | High |
| **Staff insight**: **Buy for commodity problems** (auth, payments, email). **Build for competitive advantages** (recommendation engine, matching algorithm).

## Database Trade-offs

### Normalization vs Denormalization

| Aspect | Normalized (3NF) | Denormalized |
|--------|-----------------|--------------|
| **Redundancy** | Minimal; single source of truth | Duplicated data across tables |
| **Read performance** | Slow; requires joins | Fast; single-table reads |
| **Write performance** | Slow; multiple table updates | Fast; single-table writes |
| **Consistency** | Easy; single source of truth | Hard; need sync mechanisms |
| **Staff insight**: **Denormalize for read-heavy workloads**. Use materialized views or CDC to sync denormalized data.

### Sharding vs Replication

| Aspect | Sharding | Replication |
|--------|----------|-------------|
| **Purpose** | Write scaling; data partitioning | Read scaling; high availability |
| **Complexity** | High; cross-shard queries | Low; transparent to application |
| **Consistency** | Cross-shard transactions hard | Replication lag; eventual consistency |
| **Staff insight**: **Replicate first, shard later**. Replication solves 80% of scaling problems. Sharding adds permanent complexity.

## Caching Trade-offs

### Cache-Aside vs Write-Through

| Aspect | Cache-Aside (Lazy) | Write-Through |
|--------|-------------------|---------------|
| **Read latency** | First read slow; subsequent fast | Always fast (cache is current) |
| **Write latency** | Fast (no cache update) | Slow (write to cache + DB) |
| **Consistency** | Possible stale data | Always consistent |
| **Complexity** | Simple | More complex |
| **Staff insight**: **Cache-Aside is the default**. Use Write-Through only when read consistency is critical.

### Cache Invalidation Strategies

| Strategy | Pros | Cons |
|----------|------|------|
| **TTL-based** | Simple; automatic cleanup | Possible stale data |
| **Event-driven** | Near-real-time consistency | Complex; depends on event reliability |
| **Write-through** | Always consistent | Higher write latency |
| **Staff insight**: Use **TTL + event-driven invalidation** — TTL as safety net, events for real-time updates.

## Message Queue Trade-offs

### At-least-once vs At-most-once

| Semantics | Pros | Cons |
|-----------|------|------|
| **At-least-once** | No message loss | Possible duplicates; need idempotency |
| **At-most-once** | Simple; no duplicates | Possible message loss |
| **Exactly-once** | No loss, no duplicates | Complex; performance overhead |
| **Staff insight**: **At-least-once + idempotent consumers** is the practical choice. True exactly-once is expensive and often unnecessary.

### Kafka vs RabbitMQ

| Aspect | Kafka | RabbitMQ |
|--------|-------|----------|
| **Throughput** | Millions of msg/sec | Thousands of msg/sec |
| **Persistence** | Disk-based; long retention | Memory/disk; short retention |
| **Use case** | Event streaming, log aggregation | Task queues, complex routing |
| **Ordering** | Per-partition ordering | Per-queue ordering |
| **Staff insight**: Use **Kafka for event streaming** and **RabbitMQ for task queues**. They solve different problems.

## Staff-Level Trade-off Framework

1. **Define requirements first**: What matters most? Latency, throughput, consistency, cost?
2. **Measure before optimizing**: Profile to identify actual bottlenecks
3. **Start simple**: Monolith > microservices; single DB > sharding; sync > async
4. **Add complexity only when needed**: Scale horizontally before optimizing vertically
5. **Document trade-offs**: Make architectural decisions explicit and traceable
6. **Re-evaluate periodically**: Requirements change; revisit trade-offs as system grows
7. **Consider operational cost**: Complex systems need more engineering bandwidth
8. **Plan for failure**: Every trade-off has failure modes; design for graceful degradation
