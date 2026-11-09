# Database Sharding Strategy

## Problem Statement

Design a database sharding strategy for a growing application that has outgrown a single database instance. Compare strategies: range-based, hash-based, and directory-based sharding. Address shard key selection, rebalancing, cross-shard queries, and migration from single-shard to multi-shard architecture.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Shard Key Selection**: Identify the optimal shard key based on query patterns.
- **Shard Distribution**: Even data distribution across shards to avoid hot spots.
- **Rebalancing**: Add/remove shards with minimal downtime and data movement.
- **Cross-Shard Queries**: Support queries that span multiple shards.
- **Migration Path**: Zero-downtime migration from single DB to sharded architecture.
- **Shard Routing**: Application or proxy routes queries to correct shard.

### Non-Functional Requirements
- **Linear scalability**: Adding shards increases capacity proportionally.
- **No hot shards**: Even read/write distribution across all shards.
- **Minimal cross-shard queries**: < 5% of queries span multiple shards.
- **Rebalance time**: Add shard in < 1 hour with zero downtime.
- **Data locality**: Related data co-located on the same shard.

## Key Design Decisions

- **Hash-based sharding**: Uniform distribution via `hash(shard_key) % num_shards`.
- **Virtual nodes**: 100x virtual nodes per physical shard for even distribution.
- **Consistent hashing**: Minimize data movement when adding/removing shards.
- **Proxy layer**: Vitess/ProxySQL handles shard routing transparently.
- **Application-aware sharding**: Application computes shard key for writes.

## Sharding Strategies Comparison

| Strategy | Distribution | Range Queries | Hot Spots | Rebalancing | Best For |
|----------|-------------|---------------|-----------|-------------|----------|
| Range-based | Even if data is | Native support | Yes (recent data) | Simple (split range) | Time-series, ordered data |
| Hash-based | Uniform | No | No | Complex (rehash) | User data, general purpose |
| Directory-based | Flexible | Depends | No | Update directory | Multi-tenant, complex keys |

### Range-Based Sharding

```
Shard 1: user_id 1     - 1,000,000
Shard 2: user_id 1,000,001 - 2,000,000
Shard 3: user_id 2,000,001 - 3,000,000

Pros: Range queries are fast (single shard)
Cons: Hot shard on the latest range (new users)
      Rebalancing requires splitting ranges
```

### Hash-Based Sharding

```
shard = hash(user_id) % num_shards

User 12345 → hash("12345") % 4 = Shard 2
User 67890 → hash("67890") % 4 = Shard 0

Pros: Uniform distribution, no hot spots
Cons: Range queries require scanning all shards
      Rebalancing moves ~1/N of data
```

### Consistent Hashing (Recommended)

```
Hash Ring:
  0°     Shard A (Virtual Node A1)
  90°    Shard B (Virtual Node B1)
  180°   Shard A (Virtual Node A2)
  270°   Shard C (Virtual Node C1)

User lookup: hash(user_id) → find next clockwise vnode → route to shard

Adding Shard D:
  Only moves data between affected vnodes (~1/N of total)
  Shard A1 → D1, rest stays put

Pros: Minimal data movement on rebalance
      Virtual nodes for fine-grained distribution
Cons: More complex implementation
```

## Schema Design with Sharding

### Shard Mapping Table (Directory-Based)

```sql
-- Central configuration database (not sharded)
CREATE TABLE shard_mapping (
    shard_id INT PRIMARY KEY,
    host VARCHAR(255) NOT NULL,
    port INT NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    min_user_id BIGINT,  -- For range-based
    max_user_id BIGINT,
    hash_range_start INT, -- For hash-based
    hash_range_end INT,
    status VARCHAR(20) DEFAULT 'active',
    weight DECIMAL(5,2) DEFAULT 1.00, -- For weighted distribution
    created_at TIMESTAMP DEFAULT NOW()
);

-- Example: 4 shards
INSERT INTO shard_mapping VALUES
(1, 'db-shard-1.internal', 5432, 'app_shard_1', 1, 250000000, 0, 25, 'active', 1.0),
(2, 'db-shard-2.internal', 5432, 'app_shard_2', 250000001, 500000000, 26, 50, 'active', 1.0),
(3, 'db-shard-3.internal', 5432, 'app_shard_3', 500000001, 750000000, 51, 75, 'active', 1.0),
(4, 'db-shard-4.internal', 5432, 'app_shard_4', 750000001, 1000000000, 76, 100, 'active', 1.0);
```

### Global Tables (Not Sharded)

```sql
-- These tables live in a central database, not sharded
CREATE TABLE users_global (
    user_id BIGINT PRIMARY KEY,
    shard_id INT NOT NULL,  -- Routes to correct shard
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    -- Read-only reference data; replicated to all shards or in central DB
);
```

### Shard-Local Tables (Sharded by user_id)

```sql
-- Each shard has these tables, containing only data for its user range
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    preferences JSONB
);

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id, created_at DESC);
```

## Staff-Level Design Considerations

### Shard Key Selection
- **Primary criterion**: Query patterns determine the shard key.
- **Staff insight**: The shard key is the most important decision — it's hard to change later. Choose the key that appears in 95% of WHERE clauses. For e-commerce, `user_id` is ideal because most queries are "get user's orders/profile." Never shard by a column that's rarely queried — it forces cross-shard joins.

### Virtual Nodes for Load Balancing
- **100x vnodes per shard**: Each physical shard owns ~100 virtual nodes on the hash ring.
- **Staff insight**: Without virtual nodes, adding a shard moves 25% of data (with 4 shards). With 400 virtual nodes (100 per shard), adding a shard moves only ~2.5% of data. Virtual nodes also prevent hot spots — a skewed data distribution on one vnode is averaged across 100 vnodes per shard.

### Cross-Shard Queries
- **Application-level aggregation**: Query each shard and merge results in application.
- **Staff insight**: Minimize cross-shard queries by design. If you need to query across shards frequently, your shard key is wrong. For unavoidable cross-shard queries (e.g., "global top sellers"), use a materialized view or separate analytics database. Never join across shards in SQL — it's a full table scan on every shard.

### Migration from Single to Multi-Shard
- **Dual-write strategy**: Write to both old and new DB during transition.
- **Staff insight**: 
  1. Deploy dual-write: writes go to single DB and new sharded DB.
  2. Backfill historical data to sharded DB.
  3. Switch reads to sharded DB via feature flag.
  4. Verify data consistency (checksums, row counts).
  5. Remove dual-write; stop writing to old DB.
  6. Archive old DB.
  
  Use a migration tool like Vitess `vtcopy` or custom scripts that backfill in batches (10K rows at a time) to avoid locking.

### Rebalancing Strategies
- **Online rebalancing**: Move data while serving traffic.
- **Staff insight**: Use a chunk-based migration: split data into chunks (e.g., by user_id range), migrate one chunk at a time. During migration, dual-write to both source and destination shards. After each chunk is verified, update the shard mapping. This keeps the system online throughout the rebalance. Monitor replication lag and throttle migration speed to avoid impacting production traffic.
