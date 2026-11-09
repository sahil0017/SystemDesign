# Outbox Pattern

## Overview

The outbox pattern ensures reliable event publishing alongside database transactions. For staff engineers, this is the **gold standard** for achieving **exactly-once event delivery** semantics in distributed systems.

## Problem

Without outbox pattern:
1. Update database
2. Publish event → fails
3. Data inconsistency

Or worse:
1. Publish event → succeeds
2. Update database → fails
3. Event published but data not updated; inconsistent state

## Solution

### How It Works

1. Start transaction
2. Update business data
3. Insert event to outbox table
4. Commit transaction (both succeed or both fail)
5. Poller/CDC publishes events from outbox to message queue
6. Mark event as published after successful publish

```
┌─────────────────────────────────────────────┐
│           Database Transaction               │
│  1. INSERT/UPDATE orders (...)               │
│  2. INSERT INTO outbox (event_type, payload) │
│  COMMIT                                      │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│           Outbox Poller / CDC                │
│  1. SELECT unprocessed events from outbox    │
│  2. Publish to Kafka                         │
│  3. UPDATE outbox SET processed = true       │
└─────────────────────────────────────────────┘
```

## Components

- **Outbox Table**: Stores events in same DB transaction as business data
- **Poller/CDC**: Reads and publishes events to message queue
- **Dead Letter Queue**: Handles permanently failed events

## Outbox Table Schema

```sql
CREATE TABLE outbox (
    id BIGINT PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL, -- 'order', 'payment'
    aggregate_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,     -- 'order.created', 'payment.succeeded'
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    retry_count INT DEFAULT 0
);

CREATE INDEX idx_outbox_unprocessed 
    ON outbox(processed_at, created_at) 
    WHERE processed_at IS NULL;
```

## Polling vs CDC

| Approach | Pros | Cons |
|----------|------|------|
| **Polling** | Simple; configurable interval | Additional DB load; polling delay |
| **CDC (Debezium)** | Near-real-time; no polling overhead | Requires CDC infrastructure; complex setup |

- **Staff insight**: Start with **polling** for simplicity. Migrate to **CDC** (Debezium) when throughput demands near-real-time event capture.

## Key Design Decisions

### Idempotent Consumers
- Outbox guarantees **at-least-once** delivery (poller may crash after publish but before mark)
- Consumers must be **idempotent** to handle duplicates
- **Staff insight**: Use **event ID as unique key** in consumer processing table for duplicate detection.

### Retry Strategy
- **Exponential backoff**: 1s, 5s, 30s, 5min, 30min before DLQ
- **Max retries**: 5-10 attempts before moving to dead letter queue
- **Staff insight**: Use **dead letter queue** for manual review of permanently failed events.

## Staff-Level Outbox Checklist

1. **Write outbox event in same transaction as business data**: Guarantees event is never lost
2. **Use unique event IDs**: Enable idempotent consumer processing
3. **Implement retry logic**: Poller retries failed publishes with exponential backoff
4. **Dead letter queue**: Move permanently failed events for manual review
5. **Monitor outbox lag**: Alert when unprocessed events exceed threshold
6. **Use CDC for high-throughput**: Debezium for near-real-time event capture
7. **Make consumers idempotent**: Handle duplicate events from outbox retries
8. **Test failure scenarios**: Poller crash, Kafka unavailability, DB outage

## CDC (Change Data Capture)

- Debezium
- AWS DMS
- Google Cloud Pub/Sub CDC

## Benefits

- Guaranteed event delivery
- No data inconsistency
- Transactional integrity
