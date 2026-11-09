# Uber - Architecture

## System Components

1. **API Gateway**: Entry point; authentication, rate limiting, request routing
2. **Ride Service**: Core ride lifecycle — request, match, start, complete, cancel
3. **Driver Service**: Driver management, availability, location tracking, earnings
4. **Rider Service**: Rider profiles, ride history, payment methods, preferences
5. **Matching Service**: Real-time driver-rider matching using geospatial indexing
6. **Pricing Service**: Dynamic surge pricing based on demand/supply
7. **Payment Service**: Fare calculation, payment processing, refunds, receipts
8. **Tracking Service**: Real-time GPS tracking via WebSocket
9. **Notification Service**: Push, SMS, email notifications
10. **Rating Service**: Post-ride ratings and feedback
11. **Support Service**: In-app support, trip issues, cancellations
12. **Geospatial Index (Redis Geo / S2)**: Spatial queries for nearest driver search
13. **Database (PostgreSQL + PostGIS)**: User data, trips, payments
14. **Database (Cassandra)**: Trip history, location traces
15. **Cache (Redis)**: Real-time state, driver locations, surge multipliers
16. **Message Queue (Kafka)**: Event streaming for analytics, notifications

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         Auth, Rate Limiting, Request Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │  Ride  │  │  Driver  │  │  Rider   │  │ Matching │  │  Pricing │  │Payment │
   │Service │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Event streaming for analytics, notifications │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │PostgreSQL│  │ Cassandra│  │   Redis  │  │  S2/H3   │  │ Stripe/  │  │Notific.│
   │(Users,   │  │(Trip     │  │(Driver   │  │(Spatial  │  │ Adyen    │  │Service │
   │ Trips)   │  │ history) │  │ locat.)  │  │ index)   │  │(Payment) │  │        │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
```

## Data Flow

### 1. Ride Request Flow
- Rider opens app → sends location and destination to Ride Service
- Ride Service requests fare estimate from Pricing Service
- Pricing Service calculates base fare + surge multiplier → returns estimate
- Rider confirms → Ride Service creates ride request
- Matching Service queries Redis Geo / S2 for nearby available drivers
- Matching Service selects best driver (proximity, rating, ETA)
- Driver receives ride request via WebSocket → accepts/declines
- On accept: Ride Service links rider and driver; both receive confirmation

### 2. Real-time Tracking Flow
- Driver app sends GPS coordinates every 2-5 seconds via WebSocket
- Tracking Service updates driver location in Redis Geo
- Rider app subscribes to driver location updates via WebSocket
- Tracking Service broadcasts driver position to rider
- Location traces stored in Cassandra for trip history and dispute resolution

### 3. Dynamic Pricing Flow
- Pricing Service collects demand (ride requests) and supply (available drivers) per zone
- Zones defined by S2/H3 cells (hierarchical spatial indexing)
- Surge multiplier = f(demand/supply ratio, time of day, weather, events)
- ML model predicts optimal surge price to balance supply and demand
- Surge multipliers cached in Redis with 30s TTL for fast reads

### 4. Payment Flow
- Trip completes → Ride Service calculates final fare (distance, time, surge)
- Payment Service charges rider's payment method via Stripe/Adyen
- Payment is **idempotent** — same ride_id charged only once
- Driver earnings calculated (fare - commission) → credited to driver account
- Receipt sent to rider via email/push notification

## Staff-Level Design Considerations

### Geospatial Indexing
- **Google S2**: Hierarchical cell system; efficient nearest-neighbor search
- **Uber H3**: Hexagonal grid; better for distance-based queries
- **Redis Geo**: Simple geospatial queries for small-scale nearest driver search
- **Choice**: S2/H3 for production scale; Redis Geo for prototyping

### Driver Matching Algorithm
- **Greedy matching**: Match rider with nearest available driver
- **Factors**: Proximity, ETA, driver rating, vehicle type, driver direction
- **Timeout**: If no driver accepts in 30s, expand search radius and retry
- **Staff insight**: Use **batch matching** — match multiple riders/drivers simultaneously for global optimization

### Surge Pricing Ethics
- **Transparency**: Show surge multiplier before rider confirms
- **Caps**: Maximum surge multiplier (e.g., 2.5x) to prevent price gouging
- **Cool-down**: Gradual surge reduction to avoid whipsaw effect
- **Staff insight**: Surge pricing is a **supply-side incentive**, not just revenue optimization. Communicate this to users.

### Real-time Tracking Optimization
- **Adaptive update frequency**: 2s when driver is moving; 10s when idle
- **Trajectory compression**: Store only significant position changes (Douglas-Peucker algorithm)
- **WebSocket connection pooling**: Reuse connections for multiple subscribers
