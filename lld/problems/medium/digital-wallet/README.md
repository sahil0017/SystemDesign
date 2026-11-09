# Digital Wallet

## Problem Statement

Design a digital wallet service that allows users to store money, make payments, transfer funds, view transaction history, and manage multiple payment methods.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Wallet creation**: Each user gets a unique wallet with an initial balance of zero.
- **Add money**: Fund wallet via bank transfer, credit/debit card, or UPI.
- **Payment**: Pay merchants using wallet balance; support QR code payments.
- **Transfer**: Send money to other wallet users; instant transfer.
- **Transaction history**: View all transactions with filters (date, type, amount).
- **Multiple payment methods**: Link bank accounts, cards; set default payment method.
- **Notifications**: SMS/push notifications for all transactions.

### Non-Functional Requirements
- **Security**: PCI-DSS compliance; encrypted storage of card details; fraud detection.
- **Consistency**: Strong consistency for balance updates; no double-spending.
- **Scale**: 10M+ users; 100K+ transactions per second.
- **Latency**: Payment < 500ms; transfer < 1s.

## Key Design Decisions
- **ACID transactions**: All balance updates in database transactions with SERIALIZABLE isolation.
- **Double-entry bookkeeping**: Every transaction creates two entries (debit + credit) for auditability.
- **Idempotency**: Idempotency keys on all payment APIs to prevent duplicate charges.
- **Fraud detection**: Real-time rules engine for suspicious transaction patterns.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│    Wallet    │────►│ Transaction  │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - walletId   │     │ - txnId      │
│ - name       │     │ - balance    │     │ - type       │
│ - phone      │     │ - currency   │     │ - amount     │
└──────────────┘     │ - version    │     │ - status     │
                     └──────────────┘     │ - timestamp  │
                                          └──────────────┘
```

## Staff-Level Design Considerations### Balance Consistency
- **Double-entry**: Every debit has a corresponding credit. Sum of all entries = 0. This catches bugs.
- **Staff insight**: Never update a single balance column. Use double-entry bookkeeping — it's the standard in all financial systems.

### Idempotency
- **Idempotency key**: Client generates a unique key per transaction. Server rejects duplicates.
- **Staff insight**: Network retries are inevitable. Without idempotency, a retry on "Send $100" could charge $200. This is the #1 bug in payment systems.

### Fraud Detection
- **Rules engine**: Velocity checks (N transactions in M minutes), amount thresholds, geographic anomalies.
- **Staff insight**: Start with simple rules. ML-based fraud detection is a phase 2 feature. Don't over-engineer on day 1.
