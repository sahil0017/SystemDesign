# Payment System - Database Design

## Database Strategy

- **PostgreSQL**: All financial records with ACID transactions — charges, refunds, payouts, subscriptions
- **Redis**: Idempotency keys, rate limiting, fraud score cache
- **Kafka**: Event streaming for webhooks, analytics, reconciliation

## PostgreSQL Schema

### Merchants (Multi-tenancy)
```sql
CREATE TABLE merchants (
    merchant_id BIGINT PRIMARY KEY,
    api_key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payout_schedule VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly', 'manual'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Charges
```sql
CREATE TABLE charges (
    charge_id BIGINT PRIMARY KEY,
    merchant_id BIGINT NOT NULL,
    customer_id BIGINT,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'succeeded', 'failed', 'voided', 'refunded'
    payment_method_token VARCHAR(255) NOT NULL,
    gateway_transaction_id VARCHAR(255),
    gateway_response JSONB,
    idempotency_key VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    metadata JSONB,
    fraud_score DECIMAL(5,2),
    fraud_action VARCHAR(20), -- 'allow', 'review', 'block'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);

CREATE INDEX idx_charges_merchant ON charges(merchant_id, created_at DESC);
CREATE INDEX idx_charges_status ON charges(status, created_at DESC);
CREATE INDEX idx_charges_idempotency ON charges(idempotency_key);
```

### Refunds
```sql
CREATE TABLE refunds (
    refund_id BIGINT PRIMARY KEY,
    charge_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'succeeded', 'failed'
    gateway_refund_id VARCHAR(255),
    reason VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (charge_id) REFERENCES charges(charge_id)
);

CREATE INDEX idx_refunds_charge ON refunds(charge_id);
```

### Payouts
```sql
CREATE TABLE payouts (
    payout_id BIGINT PRIMARY KEY,
    merchant_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'paid', 'failed', 'cancelled'
    bank_account_last4 VARCHAR(4),
    gateway_payout_id VARCHAR(255),
    scheduled_for DATE NOT NULL,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);

CREATE INDEX idx_payouts_merchant ON payouts(merchant_id, created_at DESC);
```

### Subscriptions
```sql
CREATE TABLE subscriptions (
    subscription_id BIGINT PRIMARY KEY,
    merchant_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    plan_id VARCHAR(100) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    interval VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'yearly'
    status VARCHAR(20) NOT NULL, -- 'active', 'cancelled', 'expired', 'past_due'
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    payment_method_token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    cancelled_at TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);

CREATE INDEX idx_subscriptions_merchant ON subscriptions(merchant_id, status);
CREATE INDEX idx_subscriptions_customer ON subscriptions(customer_id, status);
```

### Outbox (Event Reliability)
```sql
CREATE TABLE event_outbox (
    event_id BIGINT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- 'charge.succeeded', 'refund.created', etc.
    aggregate_type VARCHAR(50) NOT NULL, -- 'charge', 'refund', 'payout'
    aggregate_id BIGINT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    retry_count INT DEFAULT 0
);

CREATE INDEX idx_outbox_unprocessed ON event_outbox(processed_at, created_at) WHERE processed_at IS NULL;
```

### Webhook Endpoints
```sql
CREATE TABLE webhook_endpoints (
    endpoint_id BIGINT PRIMARY KEY,
    merchant_id BIGINT NOT NULL,
    url VARCHAR(500) NOT NULL,
    secret_hash VARCHAR(255) NOT NULL,
    events TEXT[], -- Array of event types to receive
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `idem:{idempotency_key}` | Hash | Idempotency key → charge_id + response | 24h |
| `rate:{merchant_id}:{endpoint}` | String | Per-merchant rate limit | 1min |
| `fraud:{customer_id}:score` | String | Cached fraud score | 1h |
| `fraud:{merchant_id}:velocity` | String | Transaction velocity counter | 1h |
| `fx:{currency_pair}` | String | Exchange rate cache | 5min |

## Indexes Strategy

### PostgreSQL Indexes
- **Charge lookup**: Composite index on `(merchant_id, created_at DESC)`
- **Idempotency**: Unique index on `idempotency_key`
- **Outbox processing**: Partial index on `processed_at IS NULL` for poller
- **Subscription billing**: Index on `(customer_id, status)` for recurring charges

## Staff-Level Database Considerations

### Financial Data Integrity
- **ACID transactions**: All charge/refund operations in single transaction
- **Immutable records**: Never UPDATE charge amount; create new record for adjustments
- **Audit trail**: Separate audit_log table for all financial state changes
- **Staff insight**: Use **database-level constraints** (`CHECK amount > 0`) as safety net

### Outbox Pattern
- **Same transaction**: Write charge + outbox event in one transaction
- **Poller**: Background process reads unprocessed events and publishes to Kafka
- **Idempotent publish**: Kafka message key = event_id to prevent duplicates
- **Staff insight**: Outbox pattern guarantees **exactly-once event delivery** semantics

### Idempotency
- **Unique constraint**: On `idempotency_key` column prevents duplicate charges
- **Redis cache**: Fast check before DB; stores original response for immediate return
- **TTL**: 24 hours — after that, key is expired and new charge is allowed
- **Staff insight**: Idempotency key is the **single source of truth** for duplicate detection
