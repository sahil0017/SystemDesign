# Payment System - Architecture

## System Components

1. **API Gateway**: Entry point; authentication via API keys, rate limiting, request routing
2. **Charge Service**: Core payment processing — authorize, capture, void
3. **Refund Service**: Full/partial refunds with approval workflow
4. **Payment Method Service**: Tokenization, card management, wallet integration
5. **Fraud Service**: Real-time fraud scoring with ML and rules engine
6. **Payout Service**: Merchant payouts to bank accounts with scheduling
7. **Dispute Service**: Chargeback handling, evidence submission, resolution
8. **Subscription Service**: Recurring billing, proration, dunning management
9. **Webhook Service**: Event delivery with retry, signature verification
10. **Reconciliation Service**: Daily settlement, transaction matching, reporting
11. **Currency Service**: Real-time exchange rates, multi-currency support
12. **Database (PostgreSQL)**: All financial records with ACID transactions
13. **Cache (Redis)**: Rate limiting, idempotency keys, fraud score cache
14. **Message Queue (Kafka)**: Event streaming for webhooks, analytics, reconciliation

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         API Key Auth, Rate Limiting, Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │ Charge │  │  Refund  │  │ Payment  │  │   Fraud  │  │  Payout  │  │Dispute │
   │Service │  │ Service  │  │ Method   │  │ Service  │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Events for webhooks, analytics, settlement   │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL│  │   Redis  │  │ Stripe/  │  │Webhook   │  │Recon.    │  │Currency│
   │(All      │  │(Rate     │  │ Adyen    │  │ Service  │  │ Service  │  │Service │
   │ financial│  │ limit,   │  │(Payment  │  │(Event    │  │(Settle-  │  │(FX     │
   │ records) │  │ Idem key)│  │ gateway) │  │ delivery)│  │ ment)    │  │ rates) │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Payment Charge Flow
- Client sends charge request with `idempotency_key` → API Gateway
- Idempotency check in Redis: if key exists, return cached result immediately
- Fraud Service scores transaction (ML model + rules engine)
- If fraud score > threshold: block or flag for review
- Charge Service tokenizes payment method via Stripe/Braintree
- Payment gateway authorizes charge (3D Secure if required)
- On success: Write charge record + outbox event in **same PostgreSQL transaction**
- Outbox poller publishes event to Kafka → Webhook Service delivers to merchant
- Return charge success response to client

### 2. Refund Flow
- Merchant initiates refund → Refund Service
- Validate: refund amount ≤ charge amount; charge is not already fully refunded
- Write refund record in PostgreSQL with ACID transaction
- Call payment gateway to process refund
- On success: Update charge status; publish refund event to Kafka
- Webhook Service notifies merchant of refund

### 3. Webhook Delivery Flow
- Outbox poller reads events from PostgreSQL outbox table
- Publishes to Kafka topic `payment.events`
- Webhook Service consumes from Kafka
- For each event: HTTP POST to merchant's webhook URL
- **Retry logic**: Exponential backoff (1s, 5s, 30s, 5min, 30min, 1h, 6h, 12h, 24h)
- **Signature verification**: HMAC-SHA256 signature in header for merchant to verify
- On success: Mark event as delivered; on failure: retry with backoff

### 4. Reconciliation Flow
- Daily: Payment gateway sends settlement report
- Reconciliation Service matches settlement entries with internal charge records
- Discrepancies flagged for manual review
- Merchant payouts calculated (charges - fees - refunds - chargebacks)
- Payout initiated to merchant bank account via ACH/wire

## Staff-Level Design Considerations

### Idempotency
- **Client-generated key**: UUID sent in `Idempotency-Key` header
- **Redis check**: Before processing, check if key exists → return cached result
- **Database constraint**: Unique index on `idempotency_key` in charges table
- **Staff insight**: Idempotency is **non-negotiable** for payment systems. Network retries are common.

### Outbox Pattern
- **Same transaction**: Write charge record AND outbox event in one DB transaction
- **Poller**: Background process reads outbox and publishes to Kafka
- **Guarantee**: Event is never lost — if poller crashes, it retries from last offset
- **Staff insight**: Outbox pattern is the **gold standard** for reliable event publishing. Never publish to Kafka directly from request handler.

### Fraud Detection
- **Real-time scoring**: ML model scores each transaction in <50ms
- **Rules engine**: Configurable rules (velocity checks, geo-velocity, amount thresholds)
- **Actions**: Block (auto-reject), review (hold for manual review), allow
- **Staff insight**: Use **ensemble approach** — ML model + rules engine + behavioral analysis. False positives cost customers; false negatives cost money.

### PCI-DSS Compliance
- **Tokenization**: Card data never touches your servers; use Stripe Elements/Braintree Hosted Fields
- **Token storage**: Store only tokens, not card numbers
- **Audit logging**: All access to payment data logged and monitored
- **Staff insight**: **Never store raw card data**. Use PCI-compliant tokenization providers. This reduces your PCI scope significantly.
