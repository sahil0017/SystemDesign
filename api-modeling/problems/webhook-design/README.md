# Webhook Design

## Problem Statement

Design a reliable webhook delivery system that notifies external services about events (order created, payment received) with retry logic, signature verification, and idempotency.

**Reference**: Educative.io, ByteByteGo

## Key Concepts

- **Event delivery**: POST to registered webhook URLs with event payload
- **Retry logic**: Exponential backoff (1s, 5s, 30s, 5min, 1hr, 6hr, 12hr)
- **Signature verification**: HMAC-SHA256 signature in `X-Webhook-Signature` header
- **Idempotency**: `X-Webhook-Idempotency-Key` for deduplication
- **Timeout**: 5-second request timeout; retry on timeout

## Payload Format

```json
{
  "id": "evt_123",
  "type": "order.created",
  "created_at": "2024-01-01T00:00:00Z",
  "data": {
    "order_id": "ord_456",
    "user_id": "usr_789",
    "total": 9999,
    "currency": "USD"
  }
}
```

## Staff-Level Insight

> "Webhooks are fire-and-forget with best-effort delivery."

- **Staff insight**: Use **HMAC signature** for webhook verification — client and server share a secret. Never trust webhook payloads without verifying signature. Implement **dead letter queue** for events that fail after all retries. Allow clients to **replay events** via API for missed webhooks. Use **idempotency keys** so clients can safely process duplicate deliveries.
