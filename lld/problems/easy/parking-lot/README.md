# Parking Lot

## Problem Statement (Staff-Level)

Design a multi-level parking lot system that handles multiple vehicle types, dynamic pricing, real-time availability, ticketing, payment processing, and overflow management. The system should support 10,000+ slots across 20+ levels with concurrent check-in/check-out operations.

**Reference**: AlgoMaster, HelloInterview, LLD Coding

## Requirements

### Functional Requirements
- **Multi-level support**: 20+ levels with different slot configurations per level
- **Vehicle types**: Compact, Large, Motorcycle, Handicapped, EV (with charging)
- **Dynamic pricing**: Hourly/daily rates by vehicle type; peak/off-peak pricing
- **Real-time availability**: Live slot count by type and level; nearest slot assignment
- **Ticketing**: QR code ticket on entry; scan on exit with auto-payment
- **Payment**: Cash, card, mobile wallet, subscription passes
- **Reservation**: Pre-book slots with time window; no-show handling
- **Overflow management**: Redirect to nearby lots when full
- **Admin dashboard**: Occupancy reports, revenue analytics, slot management

### Non-Functional Requirements
- **Scale**: 10,000+ slots; 1,000+ concurrent check-ins during peak hours
- **Latency**: Check-in < 2s; slot assignment < 500ms; payment < 3s
- **Availability**: 99.99% uptime; offline mode for gate operations
- **Concurrency**: Handle simultaneous check-in/check-out without slot double-booking
- **Audit trail**: All entry/exit events logged for security and billing

## Key Design Decisions
- **Slot assignment algorithm**: Nearest available + vehicle type match + handicap priority
- **Concurrency control**: Optimistic locking for slot reservation; distributed lock for payment
- **Database**: PostgreSQL for transactions; Redis for real-time availability
- **Offline mode**: Local cache at gates with sync on connectivity restore
- **Pricing engine**: Strategy pattern for dynamic pricing rules

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ParkingLot │────►│    Level     │────►│     Slot     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - levels     │     │ - slotMap    │     │ - slotType   │
│ - pricingEng │     │ - levelNum   │     │ - isOccupied │
└──────────────┘     └──────────────┘     │ - vehicle    │
           │                               └──────────────┘
           │ has
    ┌──────┴──────┐
    │   Gate      │
    ├─────────────┤
    │ - gateType  │
    │ - scanner   │
    └─────────────┘
```

## Staff-Level Design Considerations

### Slot Assignment Algorithm
- **Nearest first**: Minimize walking distance from entrance
- **Type matching**: Compact cars can use Large slots; not vice versa
- **Handicap priority**: Reserve handicap slots; enforce with camera verification
- **Staff insight**: Use **greedy algorithm** with priority queue for O(log n) slot assignment

### Concurrency Control
- **Optimistic locking**: Version column on Slot; retry on conflict
- **Distributed lock**: Redis lock for payment processing to prevent double-charge
- **Staff insight**: Slot double-booking is the #1 bug. Use **atomic compare-and-swap** for slot state transitions

### Dynamic Pricing
- **Strategy pattern**: Different pricing strategies (hourly, daily, peak, subscription)
- **Rule engine**: Configurable rules without code changes
- **Staff insight**: Pricing rules change frequently. Use **externalized configuration** (JSON/YAML) for business rules
