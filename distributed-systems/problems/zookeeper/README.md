# ZooKeeper

## Overview

Apache ZooKeeper is a distributed coordination service that provides **distributed locks**, **configuration management**, **leader election**, and **service discovery**. For staff engineers, ZooKeeper is the foundation for **distributed coordination** in systems like Kafka, Hadoop, and Solr.

## Key Concepts

| Concept | Description | Staff Insight |
|---------|-------------|---------------|
| **ZNode** | Basic unit of data in hierarchical namespace | Like files in a filesystem; stores small data (<1MB) |
| **Ephemeral ZNode** | Deleted when client session expires | Use for service discovery; auto-removes failed services |
| **Sequential ZNode** | Auto-incremented name suffix | Use for distributed locks and unique IDs |
| **Watcher** | One-time notification on ZNode change | Use for configuration changes, leader election |
| **Ensemble** | Group of ZooKeeper servers | Odd number (3 or 5) for quorum; prevents split-brain |
| **Leader** | Handles write requests; elected via ZAB | Single writer ensures consistency |
| **Follower** | Handles read requests; replicates from leader | Scale reads by adding followers |
| **Session** | Client connection to ZooKeeper | Session timeout = client failure detection |

## Use Cases

- **Configuration management**: Centralized config with change notification via watchers
- **Distributed locking**: Exclusive and read-write locks using ephemeral sequential nodes
- **Leader election**: Single leader from a group of peers using ephemeral nodes
- **Service discovery**: Register/discover services with health checks via ephemeral nodes
- **Name registration**: Centralized naming for distributed resources
- **Distributed queues**: Ordered task distribution using sequential nodes

## Consensus

- Uses **ZAB (ZooKeeper Atomic Broadcast)** protocol
- Requires **majority quorum** for writes (N/2+1)
- **Staff insight**: ZAB combines leader election with atomic broadcast. For new projects, consider **etcd** (Raft-based) as a more modern alternative.

## Key Design Decisions

### Ensemble Size
- **3 nodes**: Tolerates 1 failure; minimum for production
- **5 nodes**: Tolerates 2 failures; recommended for production
- **Staff insight**: Always use **odd number** of nodes. 4 nodes = same fault tolerance as 3, but higher write latency.

### Consistency Model
- **Sequential consistency**: Operations appear in order they were issued
- **Atomic updates**: All-or-nothing; no partial updates visible
- **Single-system image**: All clients see same data regardless of follower
- **Staff insight**: ZooKeeper provides **strong consistency** — use when you need linearizable reads.

## Staff-Level ZooKeeper Checklist

1. **Use 3 or 5 node ensemble**: Minimum 3 for production; 5 for high availability
2. **Set appropriate session timeout**: 10-30s; balance between failure detection and false positives
3. **Use ephemeral nodes for service discovery**: Auto-remove failed services
4. **Watchers are one-time**: Re-register watchers after trigger
5. **Keep data small**: ZNodes < 1MB; use for coordination, not data storage
6. **Handle session expiry**: Client reconnect and recover state
7. **Use sequential ephemeral for distributed locks**: Fair lock ordering
8. **Monitor ensemble health**: Watch for leader elections and sync latency
