# Car Rental System

## Problem Statement

Design a car rental system that allows customers to browse available vehicles, make reservations, manage rentals, handle payments, and process returns with damage assessment.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Vehicle catalog**: Browse cars by type, brand, price range, features (automatic/manual, fuel type).
- **Availability check**: Real-time availability by location and date range.
- **Reservation**: Book a car for a date range; hold for 24 hours before payment.
- **Pickup/Return**: Check-out car at pickup location; return at same or different location.
- **Payment**: Process rental fee, insurance add-ons, fuel charges, and late return fees.
- **Damage assessment**: Document pre-existing and new damage; charge accordingly.
- **Customer management**: User profiles, rental history, loyalty program.

### Non-Functional Requirements
- **Scale**: 10K+ vehicles across 500+ locations; 10K+ concurrent bookings.
- **Latency**: Availability check < 500ms; booking confirmation < 2s.
- **Concurrency**: Prevent double-booking of the same vehicle.

## Key Design Decisions
- **State machine**: Reservation states: Held → Confirmed → Active → Returned → Completed/Disputed.
- **Concurrency control**: Pessimistic locking on vehicle during booking window.
- **Pricing strategy**: Dynamic pricing based on demand, season, and rental duration.
- **Inventory management**: Per-location inventory with inter-location transfer support.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Customer   │────►│ Reservation  │────►│   Vehicle    │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - customerId │     │ - resId      │     │ - vehicleId  │
│ - name       │     │ - startDate  │     │ - brand      │
│ - licenseNum │     │ - endDate    │     │ - model      │
└──────────────┘     │ - status     │     │ - type       │
                     │ - totalPrice │     │ - location   │
                     └──────────────┘     └──────────────┘
```

## Staff-Level Design Considerations

### Double-Booking Prevention
- **Pessimistic lock**: `SELECT FOR UPDATE` on vehicle row during booking. Simple but blocks concurrent reads.
- **Optimistic lock**: Version column on vehicle availability. Retry on conflict. Better throughput.
- **Staff insight**: Use optimistic locking for high-read, low-conflict scenarios. Pessimistic locking causes deadlocks under high concurrency.

### Dynamic Pricing
- **Strategy pattern**: Different pricing strategies (weekend, holiday, seasonal, loyalty discount).
- **Staff insight**: Pricing rules change frequently. Externalize them in a configuration service, not in code.

### Damage Assessment
- **State pattern**: Vehicle state transitions (Available → Reserved → Rented → Returned → Maintenance).
- **Staff insight**: Use photo evidence with timestamps. Store in blob storage with references in the database.
