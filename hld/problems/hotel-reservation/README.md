# Hotel Reservation System

## Problem Statement

Design a distributed hotel reservation system like Booking.com that supports room search, real-time availability, booking management, payment processing, and multi-hotel inventory synchronization.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Room search**: Search by location, dates, guests, amenities, and price range.
- **Availability**: Real-time room availability across multiple hotels.
- **Booking**: Reserve rooms with guest details; hold for payment window.
- **Payment**: Process payments; handle refunds and cancellations.
- **Inventory sync**: Sync room inventory across multiple channels (website, app, OTAs).
- **Reviews**: Guest reviews and ratings for hotels and rooms.

### Non-Functional Requirements
- **Scale**: 100K+ hotels; 1M+ rooms; 100K+ bookings per day.
- **Latency**: Search < 1s; booking confirmation < 3s.
- **Consistency**: No overbooking; strong consistency for inventory.

## Key Design Decisions
- **Inventory service**: Centralized inventory with distributed locking for booking.
- **Search indexing**: Elasticsearch for room search with faceted filtering.
- **Payment saga**: Distributed transaction using saga pattern for booking + payment.
- **Cache strategy**: Cache search results; invalidate on inventory change.

## Architecture Overview

```
Client → CDN → Load Balancer → API Gateway
                            → Search Service (Elasticsearch)
                            → Booking Service
                            → Payment Service
                            → Inventory Service
                            
Booking Service → Kafka → Inventory Update → Hotel PMS (Property Management)
                    → Notification Service → Email/SMS Confirmation
```

## Staff-Level Design Considerations

### Overbooking Prevention
- **Distributed lock**: Lock room inventory during booking window (15 minutes). Release on timeout or confirmation.
- **Staff insight**: Use Redis distributed lock with TTL. If the lock holder crashes, the lock auto-releases. This prevents permanent room locks but requires fast booking confirmation.

### Inventory Synchronization
- **Event-driven**: Publish inventory changes to Kafka. All channels (website, app, OTAs) subscribe and update.
- **Staff insight**: Use the Outbox Pattern for reliable event publishing. Write the inventory change and the event to the same database transaction. A CDC process (Debezium) publishes to Kafka. This guarantees the event is never lost.

### Search Performance
- **Elasticsearch**: Index all rooms with location, amenities, and price. Faceted search for filtering.
- **Staff insight**: Availability is dynamic — don't store it in Elasticsearch. Search returns candidate rooms; the booking service checks real-time availability. This avoids stale availability data.
