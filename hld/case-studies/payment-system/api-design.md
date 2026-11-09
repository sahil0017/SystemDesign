# Payment System - API Design

## API Overview

RESTful API with JSON responses. All endpoints require authentication via API key (sk_live_... for secret, pk_live_... for publishable). All charge/refund operations require `Idempotency-Key` header.

## Charges

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/charges` | Create a charge |
| GET | `/v1/charges` | List charges (paginated) |
| GET | `/v1/charges/{charge_id}` | Get charge details |
| POST | `/v1/charges/{charge_id}/capture` | Capture authorized charge |
| POST | `/v1/charges/{charge_id}/void` | Void authorized charge |

### Create Charge Request
```json
{
  "amount": 2000,
  "currency": "usd",
  "source": "tok_visa",
  "description": "Order #123",
  "metadata": { "order_id": "123", "customer_id": "cust-456" }
}
```

## Refunds

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/charges/{charge_id}/refunds` | Create refund |
| GET | `/v1/charges/{charge_id}/refunds` | List refunds for charge |
| GET | `/v1/refunds/{refund_id}` | Get refund details |

## Payment Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/payment_methods` | Create payment method token |
| GET | `/v1/customers/{customer_id}/payment_methods` | List payment methods |
| POST | `/v1/customers/{customer_id}/payment_methods/{id}/attach` | Attach to customer |
| POST | `/v1/customers/{customer_id}/payment_methods/{id}/detach` | Detach from customer |

## Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/customers` | Create customer |
| GET | `/v1/customers/{customer_id}` | Get customer |
| PUT | `/v1/customers/{customer_id}` | Update customer |
| DELETE | `/v1/customers/{customer_id}` | Delete customer |

## Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/subscriptions` | Create subscription |
| GET | `/v1/subscriptions` | List subscriptions |
| GET | `/v1/subscriptions/{sub_id}` | Get subscription |
| PUT | `/v1/subscriptions/{sub_id}` | Update subscription |
| DELETE | `/v1/subscriptions/{sub_id}` | Cancel subscription |

## Payouts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/payouts` | Create payout |
| GET | `/v1/payouts` | List payouts |
| GET | `/v1/payouts/{payout_id}` | Get payout |
| POST | `/v1/payouts/{payout_id}/cancel` | Cancel payout |

## Disputes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/disputes` | List disputes |
| GET | `/v1/disputes/{dispute_id}` | Get dispute |
| POST | `/v1/disputes/{dispute_id}/submit` | Submit evidence |
| POST | `/v1/disputes/{dispute_id}/close` | Close dispute |

## Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/webhook_endpoints` | Create webhook endpoint |
| GET | `/v1/webhook_endpoints` | List webhook endpoints |
| DELETE | `/v1/webhook_endpoints/{id}` | Delete webhook endpoint |

### Webhook Events
- `charge.succeeded`, `charge.failed`, `charge.pending`
- `refund.created`, `refund.failed`
- `subscription.created`, `subscription.cancelled`, `subscription.expired`
- `payout.paid`, `payout.failed`
- `dispute.created`, `dispute.closed`

## Staff-Level API Design Considerations

### Idempotency
- All POST operations support `Idempotency-Key` header
- Key must be UUID format; TTL 24 hours
- Same key returns original response without re-processing

### Error Response
```json
{
  "error": {
    "code": "card_declined",
    "message": "Your card was declined.",
    "param": "source",
    "type": "card_error"
  }
}
```

### Pagination
- Cursor-based with `starting_after` and `ending_before`
- Return `has_more`, `url` for next page
- Default limit: 10; max limit: 100
