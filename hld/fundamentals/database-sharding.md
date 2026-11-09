# Database Sharding

## Overview

Sharding (horizontal partitioning) splits a large database into smaller, more manageable pieces called shards, each containing a subset of the data. For staff engineers, sharding is a **last resort** — optimize queries, add indexes, and use read replicas before sharding. Once sharded, undoing is extremely difficult.

## When to Shard

| Signal | Threshold | Action |
|--------|-----------|--------|
| **Database size** | >50-100GB on single node | Consider sharding |
| **Write throughput** | >50% CPU on writes | Shard writes horizontally |
| **Query latency** | p99 > SLA despite indexing | Shard to reduce scan scope |
| **Connection count** | >50K concurrent connections | Shard to distribute connections |
| **Disaster recovery** | Single DB is SPOF | Shard across regions |

- **Staff insight**: Before sharding, try: query optimization, covering indexes, read replicas, caching, denormalization, and archiving cold data. Sharding adds permanent complexity.

## Sharding Strategies

### Range-Based Sharding
- **How it works**: Split by key range (e.g., user_id 1-1M → Shard 1, 1M-2M → Shard 2)
- **Pros**: Range queries efficient; easy to understand; ordered data per shard
- **Cons**: **Hot spots** on boundary ranges; uneven distribution if data is skewed
- **Use case**: Time-series data, ordered logs, sequential IDs
- **Staff insight**: Range sharding creates hot spots on the latest range. Use **pre-splitting** — create future ranges in advance to distribute writes.

### Hash-Based Sharding
- **How it works**: `shard = hash(shard_key) % num_shards`
- **Pros**: Uniform distribution; no hot spots; predictable routing
- **Cons**: Range queries require scanning all shards; rebalancing is expensive (100% data move)
- **Use case**: User data, session storage, key-value stores
- **Staff insight**: Use **consistent hashing** instead of modulo to minimize data movement during rebalancing. With virtual nodes, only 1/N of data moves when adding a shard.

### Directory-Based Sharding
- **How it works**: Central lookup service maps keys to shards (shard map / routing table)
- **Pros**: Flexible routing; easy rebalancing; supports custom strategies
- **Cons**: Lookup adds latency; single point of failure (must be replicated)
- **Use case**: Complex routing rules, multi-tenant systems, geographic sharding
- **Staff insight**: Cache the shard map in application memory with TTL. Use **consistent hashing ring** as the directory for fault tolerance.

### Geographic Sharding
- **How it works**: Shard by user region (US → Shard 1, EU → Shard 2, APAC → Shard 3)
- **Pros**: Data residency compliance; low latency for local users; isolated failures
- **Cons**: Cross-region queries are slow; uneven regional load; complex sync
- **Use case**: Global SaaS platforms, GDPR compliance, multi-region deployments
- **Staff insight**: Combine geographic sharding with **hash-based sub-sharding** within each region for even distribution.

## Shard Key Selection

The shard key is the **most critical design decision** in sharding. A bad shard key is nearly impossible to fix.

| Criteria | Description | Example |
|----------|-------------|---------|
| **Even distribution** | Key should distribute data uniformly | Hash(user_id) |
| **Query patterns** | Most queries should filter by shard key | tenant_id for SaaS |
| **Minimize cross-shard** | Joins and transactions should stay within shard | user_id for user + orders |
| **Low cardinality risk** | Avoid keys with few distinct values | Not `status` (3 values) |
| **Stability** | Key should rarely change | Not `email` (users change email) |

- **Staff insight**: Choose a shard key that aligns with your **most frequent query pattern**. If queries need multiple dimensions, use **composite shard keys** or **data replication** across shards.

## Shard Allocation & Routing

### Direct Routing
- Application computes shard from key and connects directly
- **Pros**: Low latency, no intermediary
- **Cons**: Application complexity, hard to rebalance

### Proxy-Based Routing
- Proxy (Vitess, YugaByte, ShardingSphere) handles routing transparently
- **Pros**: Application unaware of sharding; easy rebalancing
- **Cons**: Proxy is a bottleneck; adds latency

### Staff Insight
- Start with **proxy-based routing** for flexibility. Migrate to direct routing only if proxy becomes a bottleneck.
- Use **connection pooling** per shard to avoid connection exhaustion.

## Challenges & Solutions

### Rebalancing
- **Problem**: Adding/removing shards requires data migration
- **Solution**: Consistent hashing minimizes movement; use **background migration** with dual-write during transition
- **Staff insight**: Plan shard count for 2-3x current growth. Over-provision shards to avoid frequent rebalancing.

### Cross-Shard Queries
- **Problem**: Joins across shards require distributed queries
- **Solution**: **Denormalize** data to keep related data on same shard; use **application-level joins**
- **Staff insight**: Design schema so that **90% of queries hit a single shard**. For analytics, use a separate data warehouse with synced data.

### Distributed Transactions
- **Problem**: ACID transactions across shards are complex and slow
- **Solution**: **Saga pattern** for eventual consistency; **2PC** for strong consistency (with performance cost)
- **Staff insight**: Avoid cross-shard transactions when possible. Use **compensating transactions** and **idempotent operations**.

### Hot Partitions
- **Problem**: Certain shards receive disproportionate traffic
- **Solution**: **Salting** — append random suffix to shard key; **sub-sharding** hot shards
- **Staff insight**: Monitor per-shard metrics. Use **auto-splitting** when a shard exceeds threshold (e.g., Vitess).

## Common Tools

| Tool | Type | Strengths | Use Case |
|------|------|-----------|----------|
| **Vitess** | MySQL sharding | Auto-sharding, resharding, global view | MySQL at scale (YouTube) |
| **YugaByteDB** | Distributed SQL | PostgreSQL-compatible, global | Global distributed SQL |
| **CockroachDB** | Distributed SQL | Auto-rebalancing, geo-partitioning | Multi-region SQL |
| **ShardingSphere** | Proxy/framework | JDBC integration, rule-based | Java ecosystem sharding |
| **MongoDB** | NoSQL sharding | Auto-sharding, chunk migration | Document-based sharding |

## Staff-Level Sharding Checklist

1. **Optimize before sharding**: Indexes, queries, caching, read replicas
2. **Choose shard key carefully**: Align with query patterns; ensure even distribution
3. **Plan for rebalancing**: Use consistent hashing; background migration
4. **Minimize cross-shard operations**: Denormalize; design for single-shard queries
5. **Handle distributed transactions**: Saga pattern; idempotent operations
6. **Monitor per-shard metrics**: Distribution, latency, throughput, error rate
7. **Test failure scenarios**: Shard failure, network partition, rebalancing under load
8. **Document shard strategy**: Routing logic, key selection rationale, migration procedures
