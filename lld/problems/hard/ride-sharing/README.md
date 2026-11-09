# Ride-Sharing Service (Uber)

## Problem Statement

Design a ride-sharing service like Uber that supports rider requests, driver matching, real-time tracking, fare estimation, payment processing, and rating system.

**Reference**: AlgoMaster, LLD Coding, HelloInterview

## Requirements

### Functional Requirements
- **Rider app**: Request ride; select ride type (Economy, Comfort, XL); set pickup and drop-off.
- **Driver app**: Go online/offline; accept/decline ride requests; navigate to rider and destination.
- **Matching**: Match rider with nearest available driver; fallback to next nearest.
- **Fare estimation**: Estimate fare before booking; calculate final fare based on distance, time, and surge.
- **Real-time tracking**: Live tracking of driver and ride; share trip status with contacts.
- **Payment**: Auto-charge rider's payment method; split fare with driver; handle tips.
- **Rating**: Rate driver and rider after trip completion.

### Non-Functional Requirements
- **Scale**: 10M+ riders; 2M+ drivers; 100K+ concurrent ride requests.
- **Latency**: Driver matching < 2s; fare estimation < 500ms; tracking updates < 1s.
- **Availability**: 99.99% uptime; graceful degradation during surge demand.

## Key Design Decisions
- **Geospatial indexing**: H3 hexagonal grid for driver location storage and nearby queries.
- **Matching algorithm**: Nearest available driver with ETA-based scoring.
- **Surge pricing**: Dynamic multiplier based on demand/supply ratio per zone.
- **WebSocket**: Real-time GPS updates for driver and rider tracking.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Rider     │────►│     Ride     │────►│    Driver    │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - riderId    │     │ - rideId     │     │ - driverId   │
│ - name       │     │ - rideType   │     │ - name       │
│ - location   │     │ - pickup     │     │ - location   │
└──────────────┘     │ - dropoff    │     │ - status     │
                     │ - status     │     │ - rating     │
                     │ - fare       │     └──────────────┘
                     │ - driverId   │
                     └──────────────┘
```

## Staff-Level Design Considerations

### Driver Matching Algorithm
- **Nearest driver**: Query drivers in rider's H3 cell, then adjacent cells, expanding outward.
- **Staff insight**: H3 (Uber's hexagonal grid) is better than GeoHash for this use case. Hexagons have uniform neighbors (6 vs variable for rectangles), making expansion queries more predictable.

### Surge Pricing
- **Supply/demand ratio**: When requests > available drivers in a zone, increase multiplier.
- **Staff insight**: Use a simple formula: surge = max(1.0, demand / supply * baseMultiplier). Cap at 2.5x to avoid customer backlash. Update every 30 seconds per zone.

### Real-Time Tracking
- **GPS pipeline**: Driver app → GPS coordinates every 5s → Kafka → WebSocket gateway → Rider app.
- **Staff insight**: Use Kafka topics partitioned by H3 cell. This ensures all messages for a ride stay on the same partition for ordering. The WebSocket gateway subscribes to the rider's current cell topic.
