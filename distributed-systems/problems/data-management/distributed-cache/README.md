# Distributed Cache

## Problem Statement

Design a distributed caching system like Redis Cluster that supports high-throughput reads/writes, data partitioning, replication, and automatic failover.

**Reference**: AlgoMaster, ByteByteGo

## Requirements

### Functional Requirements
- **Basic operations**: Get, set, delete, expire with O(1) latency.
- **Partitioning**: Automatic data distribution across nodes using consistent hashing.
- **Replication**: Master-replica topology with automatic failover.
- **Eviction**: LRU/LFU eviction policies when memory is full.
- **Persistence**: RDB snapshots and AOF (Append-Only File) for durability.

### Non-Functional Requirements
- **Scale**: 100+ nodes; 1TB+ cached data; 1M+ operations per second.
- **Latency**: P99 < 5ms for get/set operations.
- **Availability**: 99.99% uptime with automatic failover.

## Key Design Decisions
- **Consistent hashing**: Virtual nodes for even data distribution.
- **Replication**: Async replication from master to replicas; sentinel for failover.
- **Cluster protocol**: Nodes communicate via gossip protocol for membership.
- **Slot-based partitioning**: 16,384 hash slots distributed across master nodes.

## Staff-Level Design Considerations

### Slot-Based Partitioning
- **Hash slots**: Key → CRC16(key) % 16384 → slot → node. Moving slots rebalances data.
- **Staff insight**: Redis Cluster uses 16,384 slots. Each master owns a range of slots. Rebalancing moves slots between masters, not individual keys. This is more efficient than rehashing all keys.

### Replication and Failover
- **Sentinel**: Monitors masters; promotes replica to master on failure.
- **Staff insight**: Use a quorum of sentinels (3+) to prevent split-brain. The promoted replica serves stale data briefly — acceptable for cache use cases. For strong consistency, use Redis Cluster with quorum reads/writes.
