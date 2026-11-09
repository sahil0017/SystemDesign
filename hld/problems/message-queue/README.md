# Distributed Message Queue

## Problem Statement

Design a distributed message queue system like Kafka or RabbitMQ that supports high-throughput message publishing, reliable delivery, consumer groups, and message persistence.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Publish/Subscribe**: Producers publish to topics; consumers subscribe and receive messages.
- **Consumer groups**: Load balancing among consumers; each message delivered to one consumer per group.
- **Persistence**: Store messages durably; configurable retention period.
- **Ordering**: Per-partition message ordering guarantee.
- **Acknowledgments**: At-least-once and exactly-once delivery semantics.
- **Dead letter queue**: Failed messages after N retries go to DLQ.

### Non-Functional Requirements
- **Throughput**: 1M+ messages per second; 100GB+/sec data ingestion.
- **Latency**: P99 publish < 5ms; P99 consume < 10ms.
- **Durability**: No message loss on broker failure.

## Key Design Decisions
- **Partitioned log**: Topics partitioned across brokers; each partition is an append-only log.
- **Replication**: Leader-follower replication with synchronous replication (ISR).
- **Consumer offset**: Consumers track their position in partitions; stored in a separate topic.
- **Zero-copy**: Use sendfile() for zero-copy message serving.

## Architecture Overview

```
Producer → Broker (Leader Partition) → Replicate to Followers
                                    → Append to Log (disk)
                                    
Consumer Group → Broker (Leader) → Read from Log
                    → Offset Commit → __consumer_offsets topic
```

## Staff-Level Design Considerations

### Partitioned Log Design
- **Append-only**: Messages are appended to partition logs. No random writes — sequential I/O is 10x faster.
- **Staff insight**: This is why Kafka is so fast. Sequential disk writes achieve ~1GB/s on commodity hardware. Random writes achieve ~100K IOPS. The log design is the key architectural decision.

### Replication Strategy
- **ISR (In-Sync Replicas)**: Only replicas that are caught up with the leader can become the new leader.
- **Staff insight**: Use min ISR = 2 for durability. If acks=all, the producer waits for all ISR replicas. This prevents data loss on leader failure but adds latency.

### Consumer Group Coordination
- **Partition assignment**: Each partition is consumed by exactly one consumer in a group. Scale consumers ≤ partitions.
- **Staff insight**: Rebalancing is the #1 source of consumer downtime. Use static membership (Kafka 2.3+) to avoid rebalancing on temporary consumer failures.
