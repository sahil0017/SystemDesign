# Airline Management System

## Problem Statement

Design an airline management system that handles flight scheduling, seat booking, check-in, boarding, and cancellation with support for multiple airlines and airports.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Flight management**: Create, update, and cancel flights with route, schedule, and aircraft details.
- **Seat booking**: Browse available seats; select seat class (Economy, Business, First); book with passenger details.
- **Check-in**: Online and counter check-in; boarding pass generation.
- **Boarding**: Boarding group management; seat verification.
- **Cancellation/Refund**: Cancel booking with refund policy based on timing and fare type.
- **Waitlist**: Add to waitlist when flight is full; auto-assign if seats become available.
- **Baggage**: Add baggage allowance; excess baggage charges.

### Non-Functional Requirements
- **Scale**: 10K+ flights per day; 1M+ passengers; 10K+ concurrent bookings.
- **Latency**: Seat search < 500ms; booking confirmation < 2s.
- **Concurrency**: Prevent overbooking; handle simultaneous seat selection.

## Key Design Decisions
- **Seat map**: 2D grid representation with seat status (Available, Booked, Blocked, Occupied).
- **Concurrency**: Row-level locking on seat rows during booking.
- **Pricing**: Dynamic fare classes with rules for upgrades and downgrades.
- **State machine**: Booking states: Confirmed → Checked-in → Boarded → Flown / Cancelled.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Passenger   │────►│   Booking    │────►│    Flight    │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - passengerId│     │ - bookingId  │     │ - flightNum  │
│ - name       │     │ - seatClass  │     │ - origin     │
│ - passport   │     │ - status     │     │ - destination│
└──────────────┘     │ - totalPrice │     │ - departure  │
                     └──────────────┘     │ - aircraft   │
                                          └──────┬───────┘
                                                 │ has
                                          ┌──────┴───────┐
                                          │     Seat     │
                                          ├──────────────┤
                                          │ - seatNumber │
                                          │ - class      │
                                          │ - status     │
                                          └──────────────┘
```

## Staff-Level Design Considerations

### Overbooking Strategy
- **Controlled overbooking**: Airlines intentionally overbook by 5-10% based on no-show statistics.
- **Staff insight**: This is a business decision, not a bug. The system must support overbooking limits and involuntary denied boarding compensation logic.

### Seat Selection Concurrency
- **Row-level lock**: Lock the specific seat row during selection window (5 minutes).
- **Staff insight**: Use a distributed lock (Redis) with TTL. If the lock expires, the seat is released back to available.

### Dynamic Pricing
- **Fare classes**: Multiple fare classes per flight (Y, B, M, K, L) with different rules.
- **Staff insight**: Revenue management systems (like Amadeus Sabre) use complex algorithms. For LLD, a rule-based pricing engine suffices.
