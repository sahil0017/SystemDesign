# Online Food Delivery Service

## Problem Statement

Design an online food delivery service like Uber Eats or DoorDash that supports restaurant listings, menu browsing, order placement, real-time tracking, payment, and delivery management.

**Reference**: AlgoMaster, LLD Coding, HelloInterview

## Requirements

### Functional Requirements
- **Restaurant listings**: Browse restaurants by cuisine, rating, delivery time, and distance.
- **Menu browsing**: View menus with items, prices, descriptions, and availability.
- **Order placement**: Add items to cart; customize orders; place order with delivery address.
- **Order tracking**: Real-time status (Confirmed → Preparing → Picked Up → On the Way → Delivered).
- **Delivery management**: Assign delivery partners; route optimization; ETA estimation.
- **Payment**: Multiple payment methods; tips; split bills.
- **Ratings/Reviews**: Rate restaurants and delivery partners.

### Non-Functional Requirements
- **Scale**: 10K+ restaurants; 100K+ active users; 50K+ delivery partners.
- **Latency**: Restaurant search < 500ms; order placement < 2s; tracking updates < 1s.
- **Real-time**: Live order tracking with WebSocket updates.

## Key Design Decisions
- **Geospatial indexing**: R-tree or GeoHash for restaurant and delivery partner location queries.
- **State machine**: Order lifecycle with event-driven state transitions.
- **Assignment algorithm**: Nearest available delivery partner with load balancing.
- **WebSocket**: Real-time tracking updates pushed to client.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│    Order     │────►│  OrderItem   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - orderId    │     │ - menuItem   │
│ - name       │     │ - status     │     │ - quantity   │
│ - address    │     │ - restaurant │     │ - customizat │
└──────────────┘     │ - deliveryId │     └──────────────┘
                     └──────────────┘
                          │
                     ┌────┴────┐
                     │Restaurant│────►│  MenuItem  │
                     ├─────────┤     ├────────────┤
                     │ - restId│     │ - itemId   │
                     │ - name  │     │ - name     │
                     │ - rating│     │ - price    │
                     │ - location│    │ - category │
                     └─────────┘     └────────────┘
```

## Staff-Level Design Considerations

### Delivery Partner Assignment
- **Nearest neighbor**: Find the closest available delivery partner using geospatial index.
- **Staff insight**: Use GeoHash or H3 (Uber's hexagonal indexing) for efficient nearby queries. A simple distance calculation on all partners is O(n) — not scalable for 50K partners.

### Real-Time Tracking
- **WebSocket + pub/sub**: Delivery partner's GPS updates → Kafka → WebSocket gateway → customer.
- **Staff insight**: Don't poll for location updates. Use a push model. The delivery partner app sends GPS coordinates every 5 seconds to a Kafka topic; subscribers (customer app, restaurant) receive updates.

### ETA Estimation
- **Historical data**: Use average delivery time for the restaurant + current traffic data.
- **Staff insight**: Start with a simple average. Improve with ML models that consider time of day, weather, restaurant prep time, and traffic patterns. Over-estimate slightly — late deliveries hurt more than early ones.
