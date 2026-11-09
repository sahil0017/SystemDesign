# Consistency Models in Distributed Databases

## Problem Statement

Design a database architecture that supports multiple consistency levels for different operations. Implement strong consistency for financial transactions, eventual consistency for social feeds, and session consistency for user preferences. Understand CAP theorem, PACELC, quorum-based reads/writes, read-your-writes consistency, causal consistency, and vector clocks.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Strong Consistency**: Financial transactions, inventory updates, account balances.
- **Eventual Consistency**: Social feeds, product catalogs, notification counts.
- **Session Consistency**: User preferences, shopping cart, read-your-writes.
- **Causal Consistency**: Reply threads, comment chains, event ordering.
- **Quorum-Based Reads/Writes**: Configurable R/W quorum for tunable consistency.
- **Conflict Resolution**: Last-write-wins, custom merge functions, operational transformation.

### Non-Functional Requirements
- **Availability**: System remains available during network partitions.
- **Latency**: Strong consistency operations < 100ms; eventual < 10ms.
- **Scalability**: Handle 100K operations/second across multiple regions.
- **Correctness**: No lost updates for strong consistency operations.
- **Tunability**: Per-operation consistency level selection.

## Key Design Decisions

- **Multi-consistency architecture**: Different data paths for different consistency needs.
- **Synchronous replication**: For strong consistency (financial data).
- **Asynchronous replication**: For eventual consistency (feeds, catalogs).
- **Sticky sessions**: For session consistency (read-your-writes).
- **Vector clocks**: For causal ordering and conflict detection.

## Consistency Models Comparison

| Model | Read Guarantee | Write Guarantee | Latency | Availability | Use Case |
|-------|---------------|----------------|---------|-------------|----------|
| Strong | Latest write | All replicas | High | Low (during partition) | Payments, inventory |
| Session | Read-your-writes | Primary first | Medium | High | User prefs, cart |
| Causal | Causal order | Causal deps | Medium | High | Replies, comments |
| Eventual | Eventually latest | Any replica | Low | Highest | Feeds, catalogs |
| Quorum | R+Q > N | W+Q > N | Tunable | Tunable | General purpose |

### CAP Theorem

```
In a network partition (P), you must choose:
- Consistency (C): Return error if can't guarantee latest data
- Availability (A): Return stale data rather than error

Examples:
- CP: ZooKeeper, HBase, Spanner (consistency over availability)
- AP: Cassandra, Dynamo, CouchDB (availability over consistency)
- Note: PostgreSQL with sync replication is CP; with async replication is AP
```

### PACELC Theorem

```
PACELC extends CAP:
- When Partition (P): Choose Availability (A) or Consistency (C)
- Else (E) - No partition: Choose Latency (L) or Consistency (C)

Examples:
- Cassandra: PA/NC (Available during partition, No strong consistency normally)
- Spanner: PC/NC (Consistent during partition, Consistent normally)
- DynamoDB: PA/LC (Available during partition, Low latency with eventual consistency normally)
```

## Schema Design

### Strong Consistency Path (Financial Data)

```sql
-- PostgreSQL with synchronous replication
-- Consistency: Strong (linearizable)
-- Replication: Synchronous to 2 of 3 replicas (quorum)

ALTER SYSTEM SET synchronous_commit = 'on';
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 2 (standby1, standby2, standby3)';

CREATE TABLE accounts (
    account_id BIGINT PRIMARY KEY,
    balance DECIMAL(12,2) NOT NULL,
    version INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY,
    from_account BIGINT NOT NULL,
    to_account BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (from_account) REFERENCES accounts(account_id),
    FOREIGN KEY (to_account) REFERENCES accounts(account_id)
);

-- Transfer with strong consistency
BEGIN;
    SELECT balance, version FROM accounts WHERE account_id = :from FOR UPDATE;
    SELECT balance, version FROM accounts WHERE account_id = :to FOR UPDATE;
    
    UPDATE accounts SET balance = balance - :amount, version = version + 1 
    WHERE account_id = :from AND balance >= :amount;
    
    UPDATE accounts SET balance = balance + :amount, version = version + 1 
    WHERE account_id = :to;
    
    INSERT INTO transactions (from_account, to_account, amount, status) 
    VALUES (:from, :to, :amount, 'completed');
COMMIT;
-- Commit waits for synchronous ack from 2 of 3 replicas
```

### Eventual Consistency Path (Social Feed)

```cql
-- Cassandra with eventual consistency
-- Consistency: ONE for writes, ONE for reads
-- Conflict resolution: Last-write-wins (LWW)

CREATE TABLE user_feeds (
    user_id TEXT,
    post_id TEXT,
    author_id TEXT,
    content TEXT,
    created_at TIMESTAMP,
    version TIMESTAMP, -- For LWW conflict resolution
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC, post_id ASC)
  AND default_time_to_live = 604800; -- 7 days

-- Write with eventual consistency
-- cqlsh: CONSISTENCY ONE;
INSERT INTO user_feeds (user_id, post_id, author_id, content, created_at, version)
VALUES (:user_id, :post_id, :author_id, :content, NOW(), NOW());

-- Read with eventual consistency
-- cqlsh: CONSISTENCY ONE;
SELECT * FROM user_feeds WHERE user_id = :user_id LIMIT 50;

-- Background read-repair ensures eventual convergence
ALTER TABLE user_feeds WITH dclocal_read_repair_chance = 0.1;
```

### Session Consistency Path (User Preferences)

```
# Redis with sticky sessions
# Consistency: Read-your-writes via session affinity
# Fallback: Primary read for cross-session reads

# Write preferences (always to primary)
HSET user:prefs:{user_id} theme dark language en currency USD
EXPIRE user:prefs:{user_id} 2592000  # 30 days

# Read preferences (sticky session → same node has latest)
HGETALL user:prefs:{user_id}

# For non-sticky reads, read from primary replica
# Redis Cluster: use READONLY flag for replica reads, 
# but session-consistent reads go to primary
```

### Quorum-Based Consistency (Cassandra)

```cql
-- Cassandra with quorum-based reads/writes
-- Replication factor: 3
-- Write quorum: QUORUM (2 of 3)
-- Read quorum: QUORUM (2 of 3)
-- Guarantees: Strong consistency when no partition (Q+Q > N)

CREATE TABLE user_profiles (
    user_id TEXT PRIMARY KEY,
    email TEXT,
    name TEXT,
    preferences MAP<TEXT, TEXT>,
    version_counter COUNTER,
    updated_at TIMESTAMP
) WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'DC1': 3,
    'DC2': 3
};

-- Write with quorum consistency
-- cqlsh: CONSISTENCY QUORUM;
UPDATE user_profiles SET email = :email, updated_at = NOW() 
WHERE user_id = :user_id;

-- Read with quorum consistency
-- cqlsh: CONSISTENCY QUORUM;
SELECT * FROM user_profiles WHERE user_id = :user_id;

-- With RF=3 and QUORUM=2: Q_write + Q_read = 4 > 3 = N
-- This guarantees at least one replica has the latest write
```

### Vector Clocks for Causal Consistency

```
Vector Clock Format:
{ "node1": 3, "node2": 1, "node3": 2 }

Operations:
1. Increment own clock on write
2. Merge clocks on read (max of each component)
3. Compare clocks for causal ordering:
   - A < B: all components of A <= B, at least one <
   - A || B: concurrent (neither < other)
   - A = B: same version

Example:
Document version on Node1: {n1: 3, n2: 1, n3: 2}
Document version on Node2: {n1: 2, n2: 4, n3: 2}
Result: Concurrent (n1: 3>2 but n2: 1<4) → Conflict!

Resolution:
- Last-write-wins: Use physical timestamp as tiebreaker
- Custom merge: Application-defined merge function
- Manual: Present both versions to user for resolution
```

## Staff-Level Design Considerations

### Strong Consistency for Financial Data
- **Synchronous replication**: Wait for N replicas to ack before returning success.
- **Staff insight**: Strong consistency reduces availability during network partitions. Use it only where correctness is non-negotiable (payments, inventory). For PostgreSQL, use `synchronous_commit = on` with `synchronous_standby_names = 'FIRST 2 (...)'` for quorum-based sync replication. Expect 2-5x latency increase vs async replication.

### Eventual Consistency for Read-Heavy Data
- **Async replication**: Write to primary; replicas catch up eventually.
- **Staff insight**: Use eventual consistency for data where staleness is acceptable (product catalogs, social feeds, notification counts). Cassandra's read-repair mechanism ensures eventual convergence. Tune `read_repair_chance` (0.1 = 10% of reads trigger repair) based on your staleness tolerance. For truly global systems, accept that cross-region consistency is eventual — design the UI to handle stale data gracefully.

### Session Consistency via Sticky Sessions
- **Read-your-writes**: Route user's reads to the node that handled their write.
- **Staff insight**: Sticky sessions (session affinity in load balancer) provide session consistency without complex protocols. The user always reads from the replica that has their latest write. For Redis, this means pinning a user's session to one master node. For Cassandra, use `LOCAL_QUORUM` writes and reads within the same datacenter. The trade-off: if the pinned node fails, the user may see stale data until the session is remapped.

### Causal Consistency with Vector Clocks
- **Causal ordering**: If A caused B, all readers see A before B.
- **Staff insight**: Vector clocks track causal dependencies without global clocks. For collaborative editing (Google Docs), use Operational Transformation (OT) or CRDTs instead of vector clocks — they provide stronger guarantees for concurrent edits. For social media reply threads, store the parent event's vector clock with each new event to enforce causal ordering. DynamoDB's `ConditionExpression` provides causal consistency via conditional writes.

### Tunable Consistency with Quorums
- **R+W > N**: Guarantees strong consistency when no partition.
- **Staff insight**: Cassandra's per-request consistency level is the most practical approach for multi-consistency systems. Use:
  - `LOCAL_ONE` for fast, eventually consistent reads (feeds, catalogs).
  - `QUORUM` for important reads/writes (user profile, order status).
  - `ALL` for critical operations (account balance check).
  - `LOCAL_SERIAL` for conditional updates (inventory reservation).
  
  Don't use `ALL` in production — it blocks on any slow replica. `QUORUM` with RF=3 gives you strong consistency with tolerance for 1 replica failure.
