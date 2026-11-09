# Movie Ticket Booking

## Problem Statement (Staff-Level)

Design a movie ticket booking system like BookMyShow that handles movie catalog, theater management, seat selection, real-time availability, payment processing, show scheduling, and concurrent booking. The system should support 10K+ theaters, 100K+ shows/month, and prevent double-booking with real-time seat reservation.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Movie catalog**: Movie details, cast, trailer, ratings, genre filtering
- **Theater management**: Theater locations, halls, seat layout, amenities
- **Show scheduling**: Multiple shows per day; timing management; screen assignment
- **Seat selection**: Interactive seat map; seat types (normal, premium, VIP); real-time availability
- **Booking flow**: Select movie → select show → select seats → payment → confirmation
- **Payment**: Multiple payment methods; refund policy; coupon/discount codes
- **Concurrency**: Prevent double-booking; seat reservation with timeout
- **Notifications**: Booking confirmation, show reminder, cancellation alert

### Non-Functional Requirements
- **Scale**: 10K+ theaters; 100K+ shows/month; 1M+ bookings/day during peak
- **Latency**: Seat map load < 500ms; booking confirmation < 3s
- **Availability**: 99.99% uptime; graceful degradation during peak
- **Concurrency**: Prevent double-booking with distributed locking

## Key Design Decisions
- **Seat reservation**: Distributed lock with TTL (10min); release on timeout
- **Concurrency**: Optimistic locking for seat state; pessimistic locking for payment
- **Database**: PostgreSQL for transactions; Redis for real-time seat availability
- **Seat map**: JSON-based layout; cached in Redis for fast rendering

## Staff-Level Design Considerations

### Double-Booking Prevention
- **Distributed lock**: Redis lock per seat with 10min TTL
- **Optimistic locking**: Version column on Seat; retry on conflict
- **Staff insight**: Use **atomic compare-and-swap** for seat state transition from AVAILABLE to RESERVED

### Seat Map Optimization
- **JSON layout**: Store seat layout as JSON; cache in Redis
- **Real-time updates**: WebSocket for live seat availability during booking
- **Staff insight**: Pre-compute seat availability bitmap for O(1) availability check
