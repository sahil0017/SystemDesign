# Ticketmaster

## Problem Statement

Design a high-scale ticket booking system like Ticketmaster that handles millions of concurrent users attempting to purchase limited tickets for popular events, with fair queuing, fraud prevention, and real-time inventory management.

**Reference**: Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Event management**: Create events with venue, date, ticket types, and pricing tiers.
- **Seat selection**: Interactive seat map with real-time availability.
- **Virtual queue**: Fair queuing system when demand exceeds capacity.
- **Cart hold**: Temporary seat reservation (5-10 minutes) while completing purchase.
- **Payment processing**: Secure payment with multiple methods; handle failures and retries.
- **Fraud prevention**: Bot detection, purchase limits, and CAPTCHA.
- **Refund/transfer**: Process refunds and ticket transfers between users.

### Non-Functional Requirements
- **Scale**: 10M+ concurrent users for high-demand events; 100K+ transactions per second.
- **Latency**: Seat availability check < 100ms; checkout < 5s.
- **Fairness**: No user should be unfairly blocked from purchasing.
- **Reliability**: 99.99% uptime during high-demand events; no overselling.

## Key Design Decisions
- **Virtual queue**: Token-based fair queue; users wait their turn to access the booking flow.
- **Seat locking**: Distributed lock with TTL for cart holds; auto-release on timeout.
- **Inventory management**: Redis for real-time seat availability; PostgreSQL for persistence.
- **Rate limiting**: Per-user and per-IP rate limits to prevent bot abuse.

## Architecture Diagram

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Client  │───►│   CDN/WAF    │───►│  API Gateway │───►│  Services    │
└──────────┘    └──────────────┘    └──────┬───────┘    └──────┬───────┘
                                           │                   │
                                    ┌──────┴───────┐    ┌──────┴───────┐
                                    │  Virtual     │    │    Redis     │
                                    │  Queue       │    │  (Inventory) │
                                    └──────────────┘    └──────┬───────┘
                                                               │
                                                        ┌──────┴───────┐
                                                        │  PostgreSQL  │
                                                        │ (Orders)     │
                                                        └──────────────┘
```

## Staff-Level Design Considerations

### Virtual Queue Design
- **Token-based**: Users receive a queue position token; server notifies when it's their turn.
- **Staff insight**: Don't let all users hit the booking API simultaneously — it will crash. Use a virtual queue with WebSocket/SSE notifications. This is the #1 design decision for ticket booking systems.

### Overselling Prevention
- **Distributed lock**: Use Redis SETNX with TTL for seat locking. Lock expires if checkout doesn't complete.
- **Staff insight**: The classic problem is two users buying the same seat. Use atomic Redis operations (Lua script) to check availability and lock in a single operation. Never separate check and lock — it's a race condition.

### Bot Prevention
- **Multi-layer defense**: CAPTCHA, rate limiting, device fingerprinting, behavioral analysis.
- **Staff insight**: Bots are an arms race. No single technique works. Use a combination: CAPTCHA for obvious bots, rate limiting for volume attacks, and ML-based behavioral analysis for sophisticated bots. Always have a manual review queue for suspicious purchases.

### Cart Hold Timeout
- **TTL-based release**: Seats are held for 5-10 minutes; auto-release if payment doesn't complete.
- **Staff insight**: Use Redis TTL for automatic expiration. Don't use a background job to scan for expired carts — it's O(n) and slow. Redis TTL is O(1) and automatic.
