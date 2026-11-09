# Distributed Key-Value Store

## Problem Statement

Design a distributed key-value store like DynamoDB or Redis that supports high-throughput reads/writes, replication, partitioning, and strong/eventual consistency options.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Basic operations**: Get, put, delete, and exists with O(1) latency.
- **Partitioning**: Consistent hashing for data distribution across nodes.
- **Replication**: Multi-replica storage for fault tolerance.
- **Consistency**: Configurable consistency levels (strong, eventual, tunable).
- **TTL**: Time-to-live support for keys.
- **Scanning**: Range scans and full table scans.

### Non-Functional Requirements
- **Scale**: 10B+ keys; 1M+ operations per second; 100+ nodes.
- **Latency**: P99 read < 10ms; P99 write < 20ms.
- **Availability**: 99.99% uptime; automatic failover on node failure.

## Key Design Decisions
- **Consistent hashing**: Minimize data movement on node add/remove. Virtual nodes for even distribution.
- **Replication factor**: 3 replicas per key; quorum-based reads/writes (W + R > N).
- **Write-ahead log**: WAL for durability; async replication to followers.
- **Anti-entropy**: Merkle trees for background replication repair.

## Architecture Overview

```
Client → Load Balancer → KV Node (consistent hash ring)
                            → Local Store (LSM Tree / Skip List)
                            → Replication Coordinator
                            → Peer Nodes (async replication)
```

## Staff-Level Design Considerations

### Consistent Hashing
- **Virtual nodes**: Each physical node maps to 100-200 virtual nodes on the hash ring for even distribution.
- **Staff insight**: Without virtual nodes, adding/removing a node causes uneven data distribution. Virtual nodes ensure each node owns ~1/N of the data.

### LSM Tree vs B-Tree
- **LSM tree**: Better write throughput (sequential writes). Used by Cassandra, RocksDB, LevelDB.
- **B-tree**: Better read latency. Used by PostgreSQL, MySQL.
- **Staff insight**: For a write-heavy KV store, use LSM trees. Writes are appended to a memtable and flushed to SSTables on disk. Reads check memtable first, then SSTables. Compaction merges SSTables in the background.

### Quorum Consistency
- **Tunable consistency**: Client specifies consistency level (ONE, QUORUM, ALL).
- **Staff insight**: Use the Dynamo paper's quorum model: W + R > N (replication factor). This ensures at least one replica has the latest value. For N=3, W=2, R=2 gives strong consistency. W=1, R=1 gives eventual consistency.
