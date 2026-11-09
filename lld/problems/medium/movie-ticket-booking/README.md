# Movie Ticket Booking (LLD)

## Problem Statement (Staff-Level)

Design a movie ticket booking system with cinema management, show scheduling, seat selection, booking with time-limited seat locks, and payment processing using state machine and strategy patterns.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Cinema management**: Multiple halls with different seat layouts (standard, VIP, balcony).
- **Movie catalog**: Manage movies with duration, genre, rating, and cast information.
- **Show scheduling**: Create shows with time slots; avoid hall conflicts.
- **Seat selection**: Interactive seat map with real-time availability; select multiple seats.
- **Seat locking**: Lock selected seats for 10 minutes; auto-release on timeout.
- **Payment processing**: Multiple payment methods (card, wallet, UPI) with strategy pattern.
- **Ticket generation**: Generate QR code tickets with show details and seat information.

### Non-Functional Requirements
- **Scale**: 1,000+ cinemas; 100K+ concurrent bookings during peak releases.
- **Latency**: Seat availability < 100ms; booking confirmation < 3s.
- **Concurrency**: Prevent double-booking of the same seat.
- **Reliability**: Seat locks must release on timeout even if the client disconnects.

## Key Design Decisions
- **State machine**: Booking states (Selected → Locked → Paid → Confirmed / Cancelled).
- **Redis for seat locks**: Atomic SET with EXPIRE for time-limited seat reservations.
- **Strategy pattern**: Different payment methods (Card, Wallet, UPI) with a unified interface.
- **Interval tree**: For show scheduling conflict detection.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Cinema     │────►│    Hall      │────►│     Seat     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - halls      │     │ - seats[][]  │     │ - seatNumber │
│ - city       │     │ - layout     │     │ - type       │
└──────────────┘     │ - capacity   │     │ - status     │
                     └──────────────┘     └──────────────┘
                          │
                     ┌────┴────┐
                     │  Show   │
                     ├─────────┤
                     │ - time  │
                     │ - movie │
                     └─────────┘
```

## Staff-Level Design Considerations

### Seat Locking
- **Redis SET + EXPIRE**: Atomically set a seat as locked with a 10-minute TTL.
- **Release on timeout**: Redis auto-deletes the key; seat returns to available.
- **Extension**: User can extend the lock before expiry (refresh the TTL).
- **Staff insight**: Double-booking is the #1 bug. Use Redis for seat locks because of its atomic operations and TTL support. Never rely on client-side timeouts — the server must enforce the lock expiry.

### Show Scheduling
- **Conflict detection**: Use an interval tree per hall to check for time overlaps.
- **Business rules**: Minimum gap between shows (e.g., 30 minutes for cleanup).
- **Staff insight**: An interval tree makes conflict detection O(log n) instead of O(n). For a hall with 100 shows, that's 7 comparisons vs 100.

### Payment Strategy
- **Strategy pattern**: Each payment method implements a `PaymentStrategy` interface with `pay()` and `refund()`.
- **Idempotency**: Use idempotency keys to prevent duplicate charges on retry.
- **Staff insight**: The strategy pattern makes adding new payment methods trivial. Each strategy handles its own validation, API calls, and error handling. Keep the booking service decoupled from payment details.

### Booking State Machine
- **States**: Selected → Locked (10 min) → Paid → Confirmed.
- **Transitions**: Locked → Cancelled (timeout or user cancel); Paid → Refunded (cancellation).
- **Staff insight**: A state machine prevents invalid transitions (e.g., confirming an unlocked booking). Use an enum for states and enforce transitions with explicit methods. Log all state changes for audit.
