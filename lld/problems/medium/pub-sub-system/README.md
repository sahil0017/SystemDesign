# Pub/Sub System

## Problem Statement

Design a publish-subscribe messaging system that allows publishers to send messages to topics and subscribers to receive messages from topics they are interested in, with support for filtering, persistence, and backpressure.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Topics**: Publishers publish messages to named topics.
- **Subscriptions**: Subscribers subscribe to topics; receive messages in order.
- **Message filtering**: Content-based filtering; subscribers receive only matching messages.
- **Persistence**: Store messages for late-joining subscribers (replay support).
- **Multiple subscribers**: Fan-out messages to all subscribers of a topic.
- **Acknowledgments**: Subscribers acknowledge receipt; redeliver unacknowledged messages.
- **Dead letter queue**: Messages that fail delivery after N retries go to DLQ.

### Non-Functional Requirements
- **Throughput**: 100K+ messages per second per topic.
- **Latency**: Message delivery < 10ms for in-memory mode.
- **Reliability**: No message loss; at-least-once delivery guarantee.
- **Scalability**: Support 10K+ subscribers per topic.

## Key Design Decisions
- **Observer pattern**: Topic maintains list of subscribers; notifies on new messages.
- **Message queue**: Bounded queue per subscriber for backpressure handling.
- **Filter strategy**: Pluggable filter implementations (regex, JSON path, exact match).
- **Persistence**: Write-ahead log for durability; periodic compaction.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Publisher    │────►│    Topic     │────►│  Subscriber  │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - name       │     │ - name       │     │ - subscriberId│
├──────────────┤     │ - subscribers│     │ - queue      │
│ + publish()  │     │ - messageLog │     │ - filter     │
└──────────────┘     │ - dlq        │     ├──────────────┤
                     └──────────────┘     │ + onMessage()│
                                          │ + ack()      │
                                          └──────────────┘
```

## Staff-Level Design Considerations

### Backpressure Handling
- **Bounded queues**: Each subscriber has a bounded queue. When full, pause delivery.
- **Staff insight**: Without backpressure, a slow subscriber can cause OOM. Use `ArrayBlockingQueue` with `put()` (blocking) or `offer()` (drop) based on semantics.

### Delivery Guarantees
- **At-least-once**: Default. Ack + redelivery on timeout. Possible duplicates.
- **Exactly-once**: Requires idempotent consumers + transactional messaging. Complex.
- **Staff insight**: At-least-once + idempotent consumers is the practical choice. Exactly-once is a theoretical ideal that's expensive in practice.

### Message Ordering
- **Per-topic ordering**: Messages within a topic are ordered. Use a single producer thread per topic.
- **Staff insight**: Global ordering across topics is impossible in distributed systems. Per-partition ordering (like Kafka) is the practical approach.
