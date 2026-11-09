# E-commerce System - Architecture

## System Components

1. **API Gateway**: Entry point; authentication, rate limiting, request routing
2. **Catalog Service**: Product management, categories, pricing, variants
3. **Search Service**: Product search with Elasticsearch (faceting, autocomplete)
4. **Cart Service**: Shopping cart management, persistent across sessions
5. **Order Service**: Order creation, status tracking, cancellation, returns
6. **Payment Service**: Payment processing, refunds, idempotent charges
7. **Inventory Service**: Stock tracking, reservation, low-stock alerts
8. **Shipping Service**: Address validation, shipping methods, tracking
9. **Review Service**: Product reviews, ratings, Q&A, moderation
10. **Recommendation Service**: Personalized product recommendations
11. **Notification Service**: Order confirmations, shipping updates, promotions
12. **User Service**: Accounts, profiles, addresses, wishlists
13. **Database (PostgreSQL)**: Orders, payments, users (ACID transactions)
14. **Database (Cassandra)**: Product catalog, reviews (high read throughput)
15. **Cache (Redis)**: Product cache, session cart, inventory counters
16. **Search (Elasticsearch)**: Product search with faceting
17. **Message Queue (Kafka)**: Order events, inventory updates, notifications

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         Auth, Rate Limiting, Request Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │Catalog │  │   Cart   │  │   Order  │  │ Payment  │  │Inventory │  │Shipping│
   │Service │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Order events, inventory, notifications       │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL│  │ Cassandra│  │   Redis  │  │ Elastic- │  │ Stripe/  │  │Notific.│
   │(Orders,  │  │(Catalog, │  │(Cart,    │  │search    │  │ Adyen    │  │Service │
   │Payments) │  │ Reviews) │  │ Cache)   │  │(Search)  │  │(Payment) │  │        │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Product Search Flow
- User searches → Search Service queries Elasticsearch
- Elasticsearch returns products with faceting (category, price range, brand)
- Product details fetched from Cassandra/Redis cache
- Reviews aggregated from Review Service
- Recommendations fetched from Recommendation Service

### 2. Checkout Flow
- User clicks checkout → Cart Service validates cart items
- Inventory Service checks stock availability for each item
- **Stock reservation**: Inventory reserved for 15 minutes (prevents overselling)
- Order Service creates order with status "pending_payment"
- Payment Service charges user's payment method via Stripe/Adyen
- On success: Order status → "confirmed"; Inventory committed; Kafka event published
- On failure: Order status → "payment_failed"; Inventory released
- Notification Service sends order confirmation email

### 3. Order Processing Flow
- Order confirmed → Kafka event `order.confirmed`
- Inventory Service decrements stock
- Shipping Service calculates shipping method and cost
- Warehouse picks and packs order
- Shipping tracking number assigned → Kafka event `order.shipped`
- Notification Service sends shipping update to user
- Delivery confirmed → Kafka event `order.delivered`

### 4. Inventory Management Flow
- **Stock check**: Read from Redis counter (fast); fallback to PostgreSQL
- **Reservation**: On checkout, reserve stock for 15min with Redis TTL
- **Commit**: On payment success, decrement stock in PostgreSQL
- **Release**: On payment failure or timeout, release reserved stock
- **Low-stock alert**: When stock < threshold, publish alert event

## Staff-Level Design Considerations

### Preventing Overselling
- **Optimistic locking**: Version column on inventory; retry on conflict
- **Stock reservation**: Reserve during checkout; commit on payment; release on timeout
- **Redis atomic operations**: DECR with minimum value check via Lua script
- **Staff insight**: Never rely on read-then-write for inventory. Use **atomic compare-and-swap** or **database-level constraints**.

### Checkout Idempotency
- **Idempotency key**: Client-generated UUID per checkout attempt
- **Duplicate detection**: Same key returns original order without re-charging
- **Payment retry**: If payment times out, check order status before retrying
- **Staff insight**: Use **outbox pattern** for order creation — write order and event in same transaction

### Cart Persistence
- **Guest cart**: Stored in Redis with session ID; merged on login
- **Authenticated cart**: Stored in Redis with user ID; synced to PostgreSQL
- **Cart expiry**: 30-day TTL for abandoned carts
- **Staff insight**: Use **Redis Hash** for cart items — O(1) add/remove/update operations

### Search Optimization
- **Elasticsearch**: Full-text search with faceting, autocomplete, synonym support
- **Product sync**: Kafka consumer syncs Cassandra → Elasticsearch on product changes
- **Cache**: Popular search results cached in Redis with 5min TTL
- **Staff insight**: Use **edge n-gram analyzer** for type-ahead suggestions with <100ms latency
