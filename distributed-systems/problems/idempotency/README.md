# Idempotency

## Overview

Idempotency ensures that multiple identical requests have the same effect as a single request. For staff engineers, idempotency is **non-negotiable** in distributed systems — network retries, duplicate messages, and client retries are inevitable.

## Why It Matters

- **Network retries**: HTTP clients retry on timeout; server may have processed the request
- **Duplicate messages**: Kafka at-least-once delivery; message queues retry on failure
- **Load balancer retries**: LB retries on backend timeout; request may have succeeded
- **Client-side retries**: Mobile apps retry on poor network; web browsers retry on 5xx
- **Staff insight**: Design for idempotency from day one. Adding it later is expensive and error-prone.

## Implementation Strategies

### Idempotency Key
- **Client-generated UUID**: Sent in `Idempotency-Key` header
- **Server-side check**: Before processing, check if key exists → return cached result
- **Storage**: Redis (fast check) + PostgreSQL (unique constraint as safety net)
- **TTL**: 24 hours — after that, key is expired and new operation is allowed
- **Staff insight**: Idempotency key is the **single source of truth** for duplicate detection.

### Database Constraints
- **Unique constraints**: Prevent duplicate rows on retry
- **Optimistic locking**: Version column; retry on conflict
- **Version numbers**: Increment on each update; detect stale updates
- **Staff insight**: Use **unique constraints** as the safety net. Application-level checks can race.

### Message Deduplication
- **Message ID tracking**: Store processed message IDs; skip duplicates
- **Dead letter queue**: Move unprocessable messages after N retries
- **Staff insight**: For Kafka consumers, use **message ID as unique key** in processing table.

## Key Design Decisions

### Storage Strategy
- **Redis**: Fast check before processing; stores original response for immediate return
- **PostgreSQL**: Unique constraint on idempotency key; safety net if Redis is down
- **Staff insight**: Use **Redis + PostgreSQL** — Redis for speed, PostgreSQL for durability.

### TTL Management
- **Short-lived operations**: 1 hour (e.g., payment authorization)
- **Long-lived operations**: 24 hours (e.g., order creation)
- **Permanent operations**: No TTL (e.g., user registration)
- **Staff insight**: TTL should match the **business window** for retries. Too short = false duplicates; too long = wasted storage.

## Staff-Level Idempotency Checklist

1. **All POST operations should support idempotency key**: Payment, order creation, booking
2. **Use client-generated UUID**: Server-generated keys don't work for client retries
3. **Store original response**: Return cached result without re-processing
4. **Unique constraint in database**: Safety net if cache is bypassed
5. **Set appropriate TTL**: Match business retry window (1h–24h)
6. **Test duplicate scenarios**: Simulate network retries and message duplicates
7. **Document idempotency in API**: Make it explicit in API contracts
8. **Monitor idempotency hits**: High rate indicates retry storm or client bug
- Exactly-once semantics

## Best Practices

- Generate idempotency keys client-side
- Set appropriate TTL for keys
- Use atomic operations
- Log idempotency checks
