# Concert Ticket Booking System

## Problem Statement

Design a concert ticket booking system that allows users to browse events, select seats, purchase tickets, and handle high-concurrency scenarios for popular events (like Ticketmaster).

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Event management**: Create events with venue, date, time, and seating layout.
- **Seat selection**: View seat map; select individual seats or sections; see pricing tiers.
- **Booking**: Reserve seats for a limited time (10 minutes) while completing payment.
- **Payment**: Process payment; generate e-tickets with QR codes.
- **Waitlist**: Join waitlist when event is sold out; auto-notify if seats become available.
- **Cancellation**: Cancel booking with refund based on policy.
- **Resale**: Secondary market for ticket resale at face value.

### Non-Functional Requirements
- **Concurrency**: 100K+ users competing for 10K seats simultaneously (Taylor Swift scenario).
- **Latency**: Seat map load < 1s; booking confirmation < 3s.
- **Fairness**: Prevent bot-based bulk buying; ensure fair access.

## Key Design Decisions
- **Seat locking**: Distributed lock on seats during payment window with TTL.
- **Queue-based booking**: Virtual queue for high-demand events to prevent system overload.
- **Rate limiting**: Per-user rate limits to prevent bot abuse.
- **Idempotency**: Booking idempotency keys to prevent duplicate purchases.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│   Booking    │────►│    Event     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - bookingId  │     │ - eventId    │
│ - name       │     │ - status     │     │ - name       │
│ - paymentInfo│     │ - expiryTime │     │ - venue      │
└──────────────┘     │ - totalPrice │     │ - date       │
                     └──────────────┘     └──────┬───────┘
                                                  │ has
                                          ┌───────┴───────┐
                                          │     Seat      │
                                          ├───────────────┤
                                          │ - seatId      │
                                          │ - section     │
                                          │ - row, number │
                                          │ - priceTier   │
                                          │ - status      │
                                          └───────────────┘
```

## Staff-Level Design Considerations

### High-Concurrency Booking
- **Virtual queue**: When demand exceeds capacity, place users in a FIFO queue. Process in batches.
- **Staff insight**: This is the #1 challenge. Without a queue, 100K concurrent requests will crash the database. Use a token bucket to admit users in controlled batches.

### Seat Locking Strategy
- **Distributed lock with TTL**: Lock seats for 10 minutes. If payment isn't completed, release seats.
- **Staff insight**: Use Redis SETNX with expiry. On release, publish an event to notify waitlist users.

### Bot Prevention
- **Rate limiting**: Max 1 booking per user per event. CAPTCHA on booking initiation.
- **Staff insight**: Behavioral analysis (mouse movement, time on page) helps distinguish humans from bots. This is a cat-and-mouse game — expect constant new bot strategies.
