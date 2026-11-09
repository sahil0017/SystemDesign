# Digital Wallet (PayPal/Venmo-like)

## Problem Statement

Design a digital wallet system that handles user accounts, balance management, peer-to-peer transfers, merchant payments, transaction history, and fraud detection with double-entry bookkeeping and idempotent operations.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Account management**: Create and manage user wallets with KYC verification.
- **Balance management**: Double-entry bookkeeping for all transactions; no balance mutations.
- **P2P transfers**: Send money between users with instant settlement.
- **Merchant payments**: Pay merchants via QR code, link, or checkout integration.
- **Transaction history**: Immutable ledger with search and filter capabilities.
- **Idempotency**: Prevent duplicate transactions from network retries.
- **Notifications**: Real-time push/SMS notifications for transactions.

### Non-Functional Requirements
- **Scale**: 100M+ users; 1M+ transactions per second.
- **Latency**: Transfer completion < 500ms; balance query < 10ms.
- **Consistency**: Strong consistency for balances; zero lost or double-spent money.
- **Availability**: 99.99% uptime; transactions must never be lost.

## Key Design Decisions
- **Double-entry bookkeeping**: Every transaction creates debits and credits; balance is a derived sum.
- **Idempotency keys**: Client-generated unique keys prevent duplicate processing.
- **Outbox pattern**: Use database outbox for reliable event publishing after transaction commit.
- **Ledger as source of truth**: Balance is always computed from the ledger, never stored directly.

## Architecture Overview

```
User → API Gateway → Wallet Service
                    → Transaction Service (Double-entry)
                    → Ledger DB (PostgreSQL)
                    → Idempotency Store (Redis)
                    → Outbox → Kafka → Notification Service
                    → Fraud Detection → Block/Allow
```

## Staff-Level Design Considerations

### Double-Entry Bookkeeping
- **How it works**: Every transfer creates two entries: debit from sender, credit to receiver. Sum of all entries = balance.
- **Why it matters**: Balance is never mutated directly. It's always a derived value from the ledger, making it auditable and consistent.
- **Staff insight**: Double-entry is the foundation of all financial systems. Never store balance as a mutable column. Always compute it from the ledger. This eliminates the entire class of "balance drift" bugs.

### Idempotency
- **Idempotency key**: Client generates a UUID per transaction; server checks Redis before processing.
- **Return cached result**: If the key exists, return the previous result without reprocessing.
- **TTL management**: Keep idempotency keys for 24-48 hours (covers retry windows).
- **Staff insight**: Idempotency is the #1 requirement in payment systems. Network retries are inevitable. Without idempotency, a single retry can double-charge a user. Use the idempotency key pattern with Redis for O(1) deduplication.

### Transaction Consistency
- **ACID transactions**: Use database transactions for debit + credit + idempotency check.
- **Pessimistic locking**: Lock sender and receiver rows during transfer to prevent race conditions.
- **Outbox pattern**: Write events to an outbox table in the same transaction; a separate process publishes to Kafka.
- **Staff insight**: The outbox pattern is the key to reliable event publishing. Without it, you risk publishing events before the transaction commits (leading to duplicate processing) or losing events if the publish fails after the commit.

### Fraud Detection
- **Real-time rules**: Check transaction amount, velocity, and recipient reputation before processing.
- **ML scoring**: Score transactions for fraud risk using historical patterns.
- **Hold and review**: Flag suspicious transactions for manual review; release after investigation.
- **Staff insight**: Fraud detection should be async and non-blocking for the happy path. Block only high-confidence fraud; flag everything else for post-transaction review. This balances security with user experience.

### Balance Query Optimization
- **Materialized balance**: Store a denormalized balance column for fast reads; reconcile with ledger periodically.
- **Cache**: Cache balance in Redis with < 1s TTL for read-heavy paths.
- **Staff insight**: Computing balance from the ledger on every read is too slow at scale. Use a materialized balance with periodic reconciliation (e.g., nightly batch job) to ensure consistency. This is a classic read-optimization pattern.
