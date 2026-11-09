# System Design Trade-offs

This module covers common architectural trade-offs encountered in system design interviews and production systems. Each trade-off includes the options, pros/cons, decision framework, and real-world examples.

**References**: [Educative.io](https://www.educative.io/), [ByteByteGo](https://bytebytego.com/), [HelloInterview](https://www.hellointerview.com/)

## Trade-off Categories

### Data Storage

| # | Trade-off | Description |
|---|-----------|-------------|
| 1 | [SQL vs NoSQL](sql-vs-nosql/) | Relational vs non-relational databases |
| 2 | [Consistency vs Availability](consistency-vs-availability/) | CAP theorem trade-offs in practice |
| 3 | [Normalization vs Denormalization](normalization-vs-denormalization/) | Data redundancy vs query performance |
| 4 | [Row-store vs Column-store](row-store-vs-column-store/) | OLTP vs OLDS storage engines |

### Architecture

| # | Trade-off | Description |
|---|-----------|-------------|
| 5 | [Monolith vs Microservices](monolith-vs-microservices/) | Single deployment vs distributed services |
| 6 | [Sync vs Async Communication](sync-vs-async/) | REST/gRPC vs message queues |
| 7 | [Push vs Pull](push-vs-pull/) | Server-push vs client-pull data delivery |
| 8 | [REST vs gRPC](rest-vs-grpc/) | JSON/HTTP vs Protobuf/HTTP2 |
| 9 | [GraphQL vs REST](graphql-vs-rest/) | Client-specified vs fixed endpoints |
| 10 | [Event-Driven vs Request-Response](event-driven-vs-request-response/) | Async events vs sync requests |
| 11 | [Serverless vs Containers](serverless-vs-containers/) | Lambda functions vs Docker/Kubernetes |

### Scalability

| # | Trade-off | Description |
|---|-----------|-------------|
| 12 | [Horizontal vs Vertical Scaling](horizontal-vs-vertical/) | Add more machines vs bigger machines |
| 13 | [Sharding vs Replication](sharding-vs-replication/) | Data partitioning vs data copying |
| 14 | [CDN vs Origin Server](cdn-vs-origin/) | Edge caching vs centralized storage |
| 15 | [Connection Pooling](connection-pooling/) | Reuse connections vs create on demand |

### Performance

| # | Trade-off | Description |
|---|-----------|-------------|
| 16 | [Caching Strategies](caching-strategies/) | Write-through vs write-back vs cache-aside |
| 17 | [Batch vs Stream Processing](batch-vs-stream/) | Offline batch vs real-time stream processing |
| 18 | [Compression vs CPU](compression-vs-cpu/) | Reduce bandwidth vs increase compute |
| 19 | [Lazy vs Eager Loading](lazy-vs-eager/) | Load on demand vs load upfront |

### DevOps

| # | Trade-off | Description |
|---|-----------|-------------|
| 20 | [CI/CD Pipeline](ci-cd-pipeline/) | Self-hosted vs managed CI/CD, deployment strategies |
| 21 | [Observability Strategies](observability-strategies/) | Metrics vs logs vs traces, correlation, cost management |

## Decision Framework

When evaluating any trade-off, consider:

1. **Scale**: How many users, requests, and data volume?
2. **Latency requirements**: What is the acceptable response time?
3. **Consistency needs**: Strong, eventual, or session consistency?
4. **Cost**: Infrastructure, development, and operational costs.
5. **Team expertise**: What does the team know well?
6. **Time to market**: How quickly must the feature ship?
7. **Operational complexity**: Can the team maintain this in production?

## Staff-Level Insight

> "There are only two hard things in computer science: cache invalidation, naming things, and off-by-one errors." — Leon Bambrick

In practice, most trade-offs have no universally correct answer. The best choice depends on your specific context. A staff engineer doesn't memorize answers — they develop a framework for evaluating trade-offs based on requirements, constraints, and team capabilities.
