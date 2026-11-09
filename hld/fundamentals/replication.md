# Replication

## Overview

Replication maintains multiple copies of data across different servers to improve **availability**, **read scalability**, and **disaster recovery**. For staff engineers, replication is not just about copying data — it's about managing **consistency vs availability trade-offs**, **replication lag**, and **failover strategies**.

## Topologies

### Master-Slave (Primary-Replica)
- **How it works**: All writes go to the primary; replicas receive changes asynchronously or synchronously
- **Pros**: Simple architecture; no write conflicts; easy to understand; consistent writes
- **Cons**: Primary is single point of failure for writes; failover requires promotion; replication lag on reads
- **Variants**:
  - **Single-primary**: One writer, multiple readers (most common)
  - **Multi-primary**: Multiple writers (see Master-Master)
- **Staff insight**: This is the default choice for 90% of systems. Use **automatic failover** (e.g., Patroni for PostgreSQL, Orchestrator for MySQL) to reduce RTO from minutes to seconds.

### Master-Master (Multi-Master)
- **How it works**: Any node accepts writes; changes are replicated to all other nodes
- **Pros**: No single point of failure; writes available during partial outage; geographic distribution
- **Cons**: **Write conflicts** require resolution; higher latency (sync to all nodes); complex debugging
- **Conflict resolution**: Last-write-wins (LWW), first-write-wins (FWW), custom merge functions, CRDTs
- **Staff insight**: Multi-master is hard to get right. Use only when you need **write availability during network partitions**. For most cases, single-primary + fast failover is simpler and more reliable.

### Active-Active vs Active-Passive

| Mode | Description | Use Case |
|------|-------------|----------|
| **Active-Active** | Multiple primaries accept writes simultaneously | Multi-region writes, global apps |
| **Active-Passive** | Standby replica takes over on primary failure | Disaster recovery, cost efficiency |

- **Staff insight**: Active-active introduces **split-brain** risk. Use **quorum-based writes** (write to N/2+1 nodes) to prevent data loss during partitions.

## Replication Modes

### Synchronous Replication
- **How it works**: Write commits only after all (or quorum of) replicas acknowledge
- **Pros**: **Zero data loss**; strong consistency; no replication lag
- **Cons**: **Higher write latency** (bounded by slowest replica); write unavailable if replica down
- **Use case**: Financial transactions, inventory systems, any system where data loss is unacceptable
- **Staff insight**: Sync replication bounds latency by the slowest replica. Use **quorum-based sync** (e.g., write to 2 of 3 replicas) for availability + durability.

### Asynchronous Replication
- **How it works**: Primary commits immediately; replicas update in background
- **Pros**: **Low write latency**; primary unaffected by replica failures
- **Cons**: **Data loss risk** on primary failure; **replication lag** (seconds to minutes); stale reads
- **Use case**: Analytics, logging, read-heavy workloads where eventual consistency is acceptable
- **Staff insight**: Monitor **replication lag** as a key metric. Lag > 30s indicates a problem. Use **lag-aware read routing** — route consistency-sensitive reads to primary.

### Semi-Synchronous Replication
- **How it works**: Primary waits for at least one replica to acknowledge before committing
- **Pros**: **Balances safety and performance**; minimal data loss risk; better latency than full sync
- **Cons**: Still some replication lag; fallback to async if replica unavailable
- **Use case**: Production databases where data loss is unacceptable but latency matters
- **Staff insight**: This is the **sweet spot** for most production systems. MySQL semi-sync and PostgreSQL synchronous_standby_names provide this mode.

## Replication Lag

### Causes
- **Network latency**: Geographic distance between primary and replica
- **Write volume**: High write throughput overwhelms replica apply rate
- **Long transactions**: Large transactions block replica apply queue
- **Resource contention**: Replica CPU/disk I/O saturated
- **Staff insight**: Replication lag is the #1 cause of stale reads. Use **read-your-writes consistency** by routing post-write reads to primary for N seconds.

### Mitigation
- **Lag-aware routing**: Route consistency-sensitive reads to primary when lag > threshold
- **Parallel apply**: Use multiple threads to apply changes (MySQL 8.0+, PostgreSQL 16+)
- **Logical replication**: Selective replication of specific tables to reduce load
- **Staff insight**: For global applications, use **multi-region active-active** with conflict resolution instead of long-distance async replication.

## Failover Strategies

### Automatic Failover
- **Tools**: Patroni (PostgreSQL), Orchestrator (MySQL), Consul, etcd
- **Process**: Health check → detect primary failure → promote replica → update DNS/connection strings
- **RTO**: Seconds to minutes depending on implementation
- **Staff insight**: Test failover regularly. **Game days** that simulate primary failure reveal gaps in automation.

### Connection Handling
- **Connection pooling**: PgBouncer, ProxySQL handle failover transparently
- **DNS failover**: Update DNS records with low TTL (30-60s)
- **VIP failover**: Keepalived moves virtual IP to new primary
- **Staff insight**: Use **connection poolers** with automatic failover. Application-level retry logic should handle transient connection errors during failover.

## Use Cases

| Use Case | Topology | Replication Mode | Rationale |
|----------|----------|-----------------|-----------|
| **Read Scaling** | Master-Slave | Async | Offload reads; eventual consistency OK |
| **High Availability** | Master-Slave | Semi-sync | Fast failover; minimal data loss |
| **Disaster Recovery** | Active-Passive | Async | Geographic separation; cost efficient |
| **Global Writes** | Multi-Master | Sync/Quorum | Write availability in all regions |
| **Analytics** | Master-Slave | Async | Separate analytics from OLTP |

## Common Tools

| Tool | Database | Features |
|------|----------|----------|
| **Patroni** | PostgreSQL | Auto-failover, DCS integration (etcd/Consul) |
| **Orchestrator** | MySQL | Topology management, auto-failover |
| **PgBouncer** | PostgreSQL | Connection pooling, failover support |
| **ProxySQL** | MySQL | Query routing, connection pooling |
| **Vitess** | MySQL | Sharding + replication at scale |
| **CockroachDB** | Distributed SQL | Built-in replication, auto-rebalancing |

## Staff-Level Replication Checklist

1. **Choose replication mode based on RPO/RTO**: Sync for zero data loss; async for low latency
2. **Monitor replication lag**: Alert on lag > 30s; investigate root cause
3. **Implement automatic failover**: Target RTO < 30s for critical systems
4. **Test failover regularly**: Game days simulate real failures
5. **Use connection poolers**: Handle failover transparently for applications
6. **Route reads intelligently**: Lag-aware routing for consistency-sensitive reads
7. **Plan for split-brain**: Quorum-based writes prevent data corruption
8. **Document failover procedures**: Runbooks for manual intervention when automation fails
