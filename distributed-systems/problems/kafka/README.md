# Apache Kafka

## Overview

Apache Kafka is a distributed event streaming platform that handles real-time data feeds with high throughput, fault tolerance, and durability. For staff engineers, Kafka is the backbone of **event-driven architecture**, enabling **decoupled microservices**, **real-time analytics**, and **event sourcing**.

## Key Concepts

| Concept | Description | Staff Insight |
|---------|-------------|---------------|
| **Topic** | Category/name for records | Name by domain event (`user.created`), not by service |
| **Partition** | Ordered, immutable sequence of records | Partition key determines ordering; choose key carefully |
| **Producer** | Publishes records to topics | Use idempotent producer for exactly-once semantics |
| **Consumer** | Subscribes to topics and processes records | Consumer group enables horizontal scaling |
| **Consumer Group** | Load balancing among consumers | Each partition served by one consumer; scale ≤ partition count |
| **Broker** | Kafka server in a cluster | Cluster of brokers for fault tolerance |
| **Offset** | Position in partition | Commit offsets after processing; manage consumer group offsets |
| **Replication** | Copies of partitions across brokers | Replication factor = 3 for production; prevents data loss |
| **ZooKeeper/KRaft** | Cluster management | KRaft replaces ZooKeeper in Kafka 3.0+ |

## Use Cases

- **Log aggregation**: Centralized logging from distributed services
- **Metrics collection**: Real-time metrics streaming and aggregation
- **Event sourcing**: Store state changes as immutable events
- **Stream processing**: Real-time data transformation and analysis
- **Commit log**: Distributed transaction log for microservices
- **CDC (Change Data Capture)**: Database change streaming to Kafka

## Key Design Decisions

### Partitioning Strategy
- **Key-based**: Messages with same key go to same partition — per-entity ordering
- **Round-robin**: Even distribution without ordering guarantee
- **Staff insight**: Use **key-based partitioning** for per-entity consistency. Global ordering is a scalability anti-pattern.

### Delivery Semantics
- **At-least-once**: Default; possible duplicates; need idempotent consumers
- **Exactly-once**: Kafka 0.11+ with idempotent producer + transactions
- **Staff insight**: **At-least-once + idempotent consumers** is the practical choice for 95% of systems.

## Staff-Level Kafka Checklist

1. **Name topics by domain event**: `user.created`, not `UserService.user`
2. **Partition by entity key**: Ensures per-entity ordering
3. **Set replication factor = 3**: Prevents data loss on broker failure
4. **Use idempotent producers**: Prevent duplicate messages on retry
5. **Implement dead letter queues**: Handle poison messages after N retries
6. **Monitor consumer lag**: Primary metric for backpressure and scaling
7. **Schema validation**: Use Avro/Protobuf schemas to enforce message contracts
8. **Plan for rebalancing**: Consumer group rebalance on add/remove; use static membership
