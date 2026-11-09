# Payment System

## Problem Statement

Design a payment processing system like Stripe that supports multiple payment methods (credit cards, bank transfers, digital wallets), handles currency conversion, fraud detection, idempotent charges, refunds, subscriptions, and provides real-time transaction tracking at scale (1M+ transactions/day, $10B+ annual volume).

## Requirements

### Functional Requirements
- **Payment Methods**: Credit/debit cards, bank accounts (ACH), digital wallets (Apple Pay, Google Pay), crypto
- **Charge Processing**: One-time charges, recurring subscriptions, one-click payments
- **Refunds**: Full/partial refunds with automatic or manual processing
- **Currency Support**: Multi-currency charges with real-time exchange rates
- **Fraud Detection**: Real-time fraud scoring with ML-based risk assessment
- **Payouts**: Merchant payouts to bank accounts with configurable schedules
- **Disputes**: Chargeback handling, evidence submission, resolution tracking
- **Webhooks**: Real-time event notifications (charge.succeeded, charge.failed, refund.created)
- **Reconciliation**: Daily settlement reports, transaction matching, accounting integration

### Non-Functional Requirements
- **Scale**: 1M+ transactions/day; 10K+ TPS peak; sub-100ms payment processing
- **Latency**: Payment authorization < 500ms p99; webhook delivery < 5s
- **Availability**: 99.99% uptime; zero data loss for financial transactions
- **Security**: PCI-DSS Level 1 compliance; end-to-end encryption; tokenization
- **Consistency**: Strong consistency for financial records; exactly-once processing
- **Compliance**: PCI-DSS, GDPR, PSD2 (Strong Customer Authentication), AML/KYC

## Key Design Decisions
- **Idempotency**: All payment operations are idempotent via client-generated idempotency keys
- **Tokenization**: Card data never stored; tokenized via PCI-compliant provider (Stripe/Braintree)
- **Database**: PostgreSQL with ACID transactions for all financial records
- **Outbox Pattern**: Transaction and event written in same DB transaction for reliability
- **Fraud Detection**: Real-time ML scoring with rules engine; block/score/review actions
- **Webhooks**: At-least-once delivery with signature verification and retry logic
- **Multi-tenancy**: Isolated merchant data with shared infrastructure; per-merchant API keys
