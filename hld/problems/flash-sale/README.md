# Flash Sale System

## Problem Statement

Design a flash sale system that handles extreme traffic spikes (100x normal load) for limited-quantity product releases, preventing overselling, managing thundering herd problems, and ensuring fair access with sub-second checkout.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Product inventory**: Manage limited stock with atomic decrement; prevent overselling.
- **Virtual queue**: When demand exceeds capacity, place users in a fair FIFO queue.
- **Token-based access**: Pre-issue purchase tokens to control concurrency at the inventory layer.
- **Real-time countdown**: Synchronized countdown timer across all clients.
- **Bot detection**: Identify and block automated bots from hoarding inventory.
- **Order management**: Create orders atomically with inventory reservation.
- **Notification**: Notify queued users when it's their turn; SMS/email for waitlist.

### Non-Functional Requirements
- **Scale**: 10M+ concurrent users; 1M+ requests per second during sale start.
- **Latency**: Queue position update < 1s; checkout < 2s.
- **Consistency**: Zero overselling; inventory count must be accurate.
- **Fairness**: FIFO queue ordering; no user should be unfairly blocked.

## Key Design Decisions
- **Token bucket at edge**: Pre-allocate purchase tokens; only token-holders can reach the inventory service.
- **Redis for inventory**: Atomic DECR operations for stock management with Lua scripts.
- **Virtual queue**: Kafka-based FIFO queue with WebSocket push for position updates.
- **Read-heavy CDN**: Cache product pages, countdown timers, and static assets at the edge.

## Architecture Overview

```
Client → CDN (static) → API Gateway → Bot Detection
                                            → Virtual Queue (Kafka)
                                            → Token Service (Redis)
                                            → Inventory Service (Redis Lua)
                                            → Order Service → Payment
WebSocket → Queue Position Updates → Client
```

## Staff-Level Design Considerations

### Thundering Herd Prevention
- **Problem**: At sale start, 10M users hit the API simultaneously, overwhelming all services.
- **Solution**: Token-based rate limiting at the edge. Pre-issue N tokens (where N = inventory × 10). Only token-holders proceed.
- **Staff insight**: The token layer is the most critical component. It reduces the 10M concurrent requests to a manageable ~10K that actually reach the inventory service. Issue tokens via a lightweight Redis-based lottery.

### Inventory Atomicity
- **Redis Lua script**: Atomic check-and-decrement. `if stock > 0 then stock--; return 1 else return 0 end`.
- **No database for hot path**: Database is too slow for the initial inventory decrement. Use Redis as the source of truth during the sale.
- **Reconciliation**: After the sale, reconcile Redis inventory with the database for audit.
- **Staff insight**: Overselling is the #1 bug in flash sale systems. Never use a database for the hot-path inventory check. Redis Lua scripts guarantee atomicity at 100K+ ops/sec.

### Virtual Queue Design
- **Kafka-based FIFO**: Each user enqueues a join event; process in order.
- **Position tracking**: Maintain queue position in Redis; push updates via WebSocket.
- **Timeout handling**: If a user doesn't complete checkout in 5 minutes, release their spot.
- **Staff insight**: The queue is a psychological tool as much as a technical one. Showing users their position ("You are #4,523 in line") reduces refresh rates by 80% and improves UX.

### Bot Detection
- **Device fingerprinting**: Track browser fingerprints, IP reputation, and behavioral signals.
- **CAPTCHA challenge**: Trigger CAPTCHA for suspicious patterns (e.g., > 5 requests/sec).
- **Rate limiting**: Per-IP and per-device rate limits at the edge (Cloudflare/WAF).
- **Staff insight**: Bots are the #1 complaint in flash sales. Invest in bot detection at the edge layer. Use a combination of rate limiting, CAPTCHA, and behavioral analysis.

### Fairness Guarantees
- **FIFO ordering**: Queue position is determined by arrival time, not network speed.
- **Token lottery**: If tokens are limited, use a random lottery among early arrivals, not first-come-first-served.
- **Staff insight**: Perceived fairness matters more than actual fairness. Communicate the rules clearly and log all decisions for audit.
