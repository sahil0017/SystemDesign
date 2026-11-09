# Message Queues

## Overview

Message queues enable asynchronous communication between services, providing **decoupling**, **buffering**, and **reliable delivery**. For staff engineers, message queues are the backbone of event-driven architectures, enabling **loose coupling**, **backpressure handling**, and **event sourcing** patterns.

## Patterns

### Point-to-Point (Queue)
- **How it works**: Producer sends to queue; one consumer processes each message
- **Delivery**: Each message consumed by exactly one consumer (competing consumers)
- **Use case**: Task distribution, job processing, work distribution
- **Staff insight**: Use for **work distribution** where each task should be processed once. Scale consumers horizontally to increase throughput.

### Publish-Subscribe (Topic)
- **How it works**: Producer publishes to topic; all subscribers receive the message
- **Delivery**: Each subscriber gets a copy; independent consumption
- **Use case**: Event notification, audit logging, fan-out processing
- **Staff insight**: Use for **event broadcasting** where multiple services react to the same event. Each subscriber has independent offset tracking.

### Request-Reply
- **How it works**: Client sends request to queue; worker processes and sends reply to callback queue
- **Use case**: Async RPC, distributed computing
- **Staff insight**: Use **correlation ID** to match requests with replies. Set timeouts to handle worker failures.

### Work Queue
- **How it works**: Multiple consumers compete for messages; each message processed once
- **Use case**: CPU-intensive tasks, batch processing
- **Staff insight**: Use **priority queues** for urgent tasks. Implement **dead letter queues** for poison messages.

## Key Concepts

| Concept | Description | Staff Insight |
|---------|-------------|---------------|
| **Producer** | Sends messages to broker | Implement retry with exponential backoff; use idempotent keys |
| **Consumer** | Receives and processes messages | Acknowledge only after successful processing; handle poison messages |
| **Broker** | Manages message routing and persistence | Monitor broker health; plan for broker failure |
| **Topic/Queue** | Message destination | Name topics by domain event (e.g., `user.created`), not by service |
| **Acknowledgment** | Consumer confirms processing | Use manual ack; auto-ack risks message loss on crash |
| **Partition** | Divides topic for parallelism | Partition key determines ordering; choose key carefully |
| **Offset** | Position in partition | Commit offsets after processing; manage consumer group offsets |
| **Consumer Group** | Load balancing among consumers | Each partition served by one consumer in group; scale ≤ partition count |

## Delivery Semantics

| Semantics | Description | Implementation | Trade-off |
|-----------|-------------|----------------|-----------|
| **At-most-once** | Message delivered once or not at all | Fire-and-forget, auto-ack | Possible message loss |
| **At-least-once** | Message delivered one or more times | Manual ack, retry on failure | Possible duplicates; need idempotency |
| **Exactly-once** | Message delivered exactly once | Transactional messaging, idempotent consumers | Complex; performance overhead |

- **Staff insight**: **At-least-once + idempotent consumers** is the practical choice for 95% of systems. True exactly-once is expensive and often unnecessary. Design consumers to be **idempotent** — same message processed multiple times has same effect as once.

## Message Ordering

- **Global ordering**: All messages across topic in order — requires single partition (bottleneck)
- **Partition ordering**: Messages within a partition are ordered — most common approach
- **Key-based ordering**: Messages with same key go to same partition — per-entity ordering
- **Staff insight**: Global ordering is a **scalability anti-pattern**. Use **key-based ordering** for per-entity consistency (e.g., all user events ordered by user_id).

## Backpressure Handling

- **Problem**: Consumers can't keep up with producer rate
- **Solutions**:
  - **Queue buffering**: Messages wait in queue until consumed
  - **Rate limiting**: Producers throttle based on queue depth
  - **Consumer scaling**: Auto-scale consumers based on lag
  - **Dead letter queue**: Move unprocessable messages aside
- **Staff insight**: Monitor **consumer lag** as the primary backpressure metric. Auto-scale consumers when lag exceeds threshold. Use **DLQ** for messages that fail after N retries.

## Event-Driven Architecture Patterns

### Event Sourcing
- **How it works**: Store state changes as immutable events; reconstruct state by replaying events
- **Benefits**: Full audit trail; temporal queries; easy debugging
- **Staff insight**: Use **CQRS** (Command Query Responsibility Segregation) with event sourcing. Commands write events; queries read from materialized views.

### CQRS (Command Query Responsibility Segregation)
- **How it works**: Separate read and write models; async sync between them
- **Benefits**: Independent scaling; optimized read/write models
- **Staff insight**: CQRS adds complexity. Use only when read and write patterns are **fundamentally different** (e.g., write-heavy event sourcing with complex read queries).

### Saga Pattern
- **How it works**: Long-running transaction coordinated via events
- **Types**: Choreography (event-driven) vs Orchestration (coordinator-driven)
- **Staff insight**: Use **orchestration** for complex workflows with clear state machines. Use **choreography** for simple, well-understood event flows.

## Common Tools

| Tool | Type | Strengths | Use Case |
|------|------|-----------|----------|
| **Kafka** | Event streaming | High throughput, persistence, replay, partitions | Event sourcing, log aggregation, real-time analytics |
| **RabbitMQ** | Message broker | Flexible routing, AMQP, plugins, management UI | Task queues, complex routing, enterprise integration |
| **Amazon SQS** | Managed queue | Simple, scalable, FIFO option, integrated | AWS-native workloads, simple queues |
| **Amazon SNS** | Pub/Sub | Fan-out, multi-protocol, managed | Event notification, multi-channel delivery |
| **Apache Pulsar** | Cloud-native messaging | Multi-tenant, geo-replication, layered storage | Multi-tenant platforms, global messaging |
| **Redis Streams** | In-memory streams | Low latency, Lua scripting, pub/sub | Real-time processing, simple event streams |

## Staff-Level Message Queue Checklist

1. **Choose at-least-once + idempotent consumers**: Simpler than exactly-once; design for duplicates
2. **Name topics by domain event**: `user.created`, not `UserService.user`
3. **Partition by entity key**: Ensures per-entity ordering without global ordering bottleneck
4. **Implement dead letter queues**: Handle poison messages after N retries
5. **Monitor consumer lag**: Primary metric for backpressure and scaling decisions
6. **Set message TTL**: Prevent indefinite queue growth for unprocessable messages
7. **Schema validation**: Use Avro/Protobuf schemas to enforce message contracts
8. **Plan for broker failure**: Use replicated brokers; test consumer failover
