# Hotel Management System

## Problem Statement

Design a hotel management system that handles room booking, check-in/check-out, room service, billing, and housekeeping management.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Room management**: Multiple room types (Single, Double, Suite, Presidential) with amenities.
- **Booking**: Search availability by date range and room type; make reservations with guest details.
- **Check-in/Check-out**: Assign rooms on check-in; process check-out with bill settlement.
- **Room service**: Order food/items to room; track delivery status.
- **Billing**: Room charges, extra services, taxes, and discounts; generate invoices.
- **Housekeeping**: Track room cleanliness status; assign cleaning tasks.
- **Cancellation**: Cancel bookings with refund policy based on timing.

### Non-Functional Requirements
- **Scale**: 500+ rooms; 1K+ concurrent bookings during peak season.
- **Latency**: Room search < 300ms; check-in < 1s.
- **Concurrency**: Prevent overbooking; handle simultaneous check-ins.

## Key Design Decisions
- **State machine**: Room states: Clean → Booked → Occupied → Dirty → Clean.
- **Booking calendar**: Interval tree for efficient overlap detection in date ranges.
- **Pricing strategy**: Dynamic pricing based on occupancy, season, and advance booking.
- **Concurrency**: Pessimistic locking on room availability during booking window.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Guest     │────►│   Booking    │────►│     Room     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - guestId    │     │ - bookingId  │     │ - roomId     │
│ - name       │     │ - checkIn    │     │ - type       │
│ - contact    │     │ - checkOut   │     │ - floor      │
└──────────────┘     │ - status     │     │ - status     │
                     │ - totalPrice │     │ - amenities  │
                     └──────────────┘     └──────────────┘
```

## Staff-Level Design Considerations

### Overbooking Prevention
- **Interval tree**: O(log n) overlap detection for date range queries.
- **Staff insight**: A simple date range scan is O(n) per room × O(n) rooms. Interval tree reduces this to O(log n + k) where k is the number of overlaps.

### Room State Management
- **State pattern**: Clean → Booked → Occupied → Dirty → Clean. Housekeeping transitions Dirty → Clean.
- **Staff insight**: Never allow Occupied → Clean directly. The Dirty state ensures housekeeping is tracked.

### Dynamic Pricing
- **Revenue management**: Higher prices during high demand; early-bird discounts.
- **Staff insight**: Use a pricing engine with externalized rules. Hotels change prices daily based on competitor rates and occupancy — hardcoding is not viable.
