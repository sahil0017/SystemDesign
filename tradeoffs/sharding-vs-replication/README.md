# Sharding vs Replication

## Trade-off Overview

Sharding partitions data across multiple databases. Replication copies data to multiple databases. They solve different problems and are often used together.

## Sharding
- **Pros**: Scales writes, distributes load, no single bottleneck.
- **Cons**: Cross-shard queries are hard, rebalancing is complex, hot shards.
- **Use when**: Write throughput exceeds single-node capacity.

## Replication
- **Pros**: Read scaling, high availability, disaster recovery.
- **Cons**: Replication lag, write bottleneck on primary, data consistency.
- **Use when**: Read throughput exceeds single-node capacity.

## Staff-Level Insight

> "Replication scales reads. Sharding scales writes. Use both for maximum scale."

- **Staff insight**: Start with **replication** — add read replicas to handle read load. When writes become the bottleneck, add **sharding**. Use **consistent hashing** for sharding to minimize data movement during rebalancing. Choose shard key carefully — it determines data distribution and query patterns. Never shard by a field that's frequently used in cross-shard queries.
