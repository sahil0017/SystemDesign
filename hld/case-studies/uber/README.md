# Uber

## Problem Statement

Design a ride-sharing platform like Uber that connects riders with drivers in real-time, handles dynamic pricing, route optimization, payment processing, and supports millions of concurrent trips across multiple cities.

## Requirements

### Functional Requirements
- **User Management**: Rider and driver registration, profile management, vehicle verification
- **Ride Request**: Rider requests ride with pickup/dropoff location; system matches with nearest driver
- **Real-time Tracking**: Live GPS tracking of rider and driver positions
- **Dynamic Pricing**: Surge pricing based on demand/supply ratio in real-time
- **Payment Processing**: Multiple payment methods, fare calculation, tipping, receipts
- **Rating System**: Mutual rating and feedback after each trip
- **Driver Management**: Driver onboarding, document verification, earnings dashboard
- **Trip History**: Past trips, receipts, expense reports
- **Support**: In-app support, trip cancellation, issue reporting

### Non-Functional Requirements
- **Scale**: 10M+ daily trips; 5M+ concurrent users; 100K+ active drivers
- **Latency**: Driver matching < 2 seconds; location update < 500ms; fare estimate < 1s
- **Availability**: 99.99% uptime for ride booking; 99.9% for non-critical features
- **Accuracy**: GPS location accuracy < 10 meters; fare calculation within 1% of actual
- **Real-time**: Location updates every 2-5 seconds; WebSocket for live tracking
- **Global**: Multi-city, multi-country deployment with local compliance

## Key Design Decisions
- **Geospatial Indexing**: Google S2 / Uber H3 for spatial partitioning and nearest driver search
- **Matching Algorithm**: Greedy matching with proximity, ETA, and driver rating as factors
- **Real-time Tracking**: WebSocket for live location; Redis Geo for spatial queries
- **Dynamic Pricing**: Time-series demand/supply data with ML-based surge multiplier
- **Database**: PostgreSQL with PostGIS for user data; Cassandra for trip history; Redis for real-time state
- **Payment**: Stripe/Adyen integration with idempotent charge operations
- **Microservices**: Ride service, driver service, pricing service, payment service, notification service
