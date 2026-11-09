# Ride-Sharing Database Schema Design

## Problem Statement

Design a comprehensive database schema for a ride-sharing platform (like Uber/Lyft) that supports drivers, riders, rides, ratings, payments, surge pricing zones, and trip history. The schema must handle real-time ride matching, fare calculation with dynamic pricing, and a two-sided rating system.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Users**: Riders and drivers share a user base with different roles and profiles.
- **Drivers**: Vehicle info, license, status (online/offline/on_trip), location, acceptance rate.
- **Rides**: Ride lifecycle (requested → matched → arrived → in_progress → completed → cancelled), pickup/dropoff, fare.
- **Ride Matching**: Match rider with nearest available driver.
- **Fare Calculation**: Base fare + distance + time + surge multiplier + tolls.
- **Ratings**: Rider rates driver, driver rates rider (1-5 stars + comment).
- **Payments**: Payment methods, ride charges, tips, refunds.
- **Surge Pricing**: Dynamic pricing zones based on demand/supply ratio.

### Non-Functional Requirements
- **Low latency**: Ride matching in < 2 seconds.
- **Geospatial queries**: Find nearby drivers in < 100ms.
- **Data integrity**: Fare calculation is immutable after ride completion.
- **Scalability**: Handle 100K concurrent rides across multiple cities.
- **Audit trail**: Complete ride history for disputes and analytics.

## Key Design Decisions

- **Unified users table**: Riders and drivers share `users` table; role-specific data in separate tables.
- **Geospatial indexing**: Use PostGIS for location-based queries (nearest driver, ETA).
- **Immutable ride records**: Once completed, fare and route are never updated; refunds create new records.
- **Surge multiplier stored**: Capture surge at ride request time, not at completion.
- **Rating aggregation**: Pre-compute average rating to avoid real-time aggregation.

## Schema Design

### Core Tables

```sql
-- Users (shared by riders and drivers)
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    profile_picture_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Drivers
CREATE TABLE drivers (
    driver_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'offline', -- 'offline', 'online', 'on_trip'
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    vehicle_year INT,
    license_plate VARCHAR(20) NOT NULL,
    vehicle_color VARCHAR(20),
    driver_license_number VARCHAR(50) NOT NULL,
    insurance_expiry DATE NOT NULL,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_trips INT DEFAULT 0,
    acceptance_rate DECIMAL(5,2) DEFAULT 0.00,
    cancellation_rate DECIMAL(5,2) DEFAULT 0.00,
    current_location POINT, -- PostGIS
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Rides
CREATE TABLE rides (
    ride_id BIGINT PRIMARY KEY,
    rider_id BIGINT NOT NULL,
    driver_id BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'requested',
    -- 'requested', 'matched', 'arrived', 'in_progress', 'completed', 'cancelled'
    pickup_location POINT NOT NULL,      -- PostGIS
    dropoff_location POINT NOT NULL,     -- PostGIS
    estimated_distance_meters INT,
    estimated_duration_seconds INT,
    actual_distance_meters INT,
    actual_duration_seconds INT,
    base_fare DECIMAL(10,2),
    distance_fare DECIMAL(10,2),
    time_fare DECIMAL(10,2),
    surge_multiplier DECIMAL(3,2) DEFAULT 1.00,
    tolls DECIMAL(10,2) DEFAULT 0.00,
    fees DECIMAL(10,2) DEFAULT 0.00,
    total_fare DECIMAL(10,2),
    cancellation_reason VARCHAR(255),
    cancelled_by VARCHAR(20), -- 'rider', 'driver', 'system'
    requested_at TIMESTAMP DEFAULT NOW(),
    matched_at TIMESTAMP,
    arrived_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES users(user_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- Ratings
CREATE TABLE ride_ratings (
    rating_id BIGINT PRIMARY KEY,
    ride_id BIGINT NOT NULL,
    rater_id BIGINT NOT NULL,
    ratee_id BIGINT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (ride_id, rater_id, ratee_id),
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id),
    FOREIGN KEY (rater_id) REFERENCES users(user_id),
    FOREIGN KEY (ratee_id) REFERENCES users(user_id)
);

-- Payments
CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    ride_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'credit_card', 'paypal', 'cash', 'wallet'
    status VARCHAR(20) NOT NULL, -- 'pending', 'completed', 'refunded', 'failed'
    provider_transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Payment Methods
CREATE TABLE payment_methods (
    payment_method_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'credit_card', 'debit_card', 'paypal', 'wallet'
    last_four VARCHAR(4),
    brand VARCHAR(50),
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Surge Pricing Zones
CREATE TABLE surge_zones (
    zone_id BIGINT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    zone_polygon POLYGON NOT NULL, -- PostGIS polygon defining the zone
    multiplier DECIMAL(3,2) DEFAULT 1.00,
    demand_count INT DEFAULT 0,
    supply_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Driver Location History (for tracking and disputes)
CREATE TABLE driver_location_history (
    history_id BIGINT PRIMARY KEY,
    driver_id BIGINT NOT NULL,
    ride_id BIGINT,
    location POINT NOT NULL,
    speed_kmh DECIMAL(5,2),
    recorded_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (ride_id) REFERENCES rides(ride_id)
);
```

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `drivers` | GiST on `current_location` | Geospatial nearest-neighbor search |
| `drivers` | `(status, current_location)` | Find available drivers near location |
| `rides` | `(rider_id, requested_at DESC)` | Rider's ride history |
| `rides` | `(driver_id, requested_at DESC)` | Driver's ride history |
| `rides` | `(status, requested_at DESC)` | Active rides monitoring |
| `rides` | `(requested_at)` | Ride volume analytics |
| `ride_ratings` | `(ride_id)` | Get ratings for a ride |
| `payments` | `(ride_id)` | Payment lookup by ride |
| `driver_location_history` | `(driver_id, recorded_at DESC)` | Trip route reconstruction |
| `surge_zones` | GiST on `zone_polygon` | Point-in-polygon surge lookup |

## Staff-Level Design Considerations

### Geospatial Indexing
- **PostGIS GiST index**: Enables `ST_DWithin()` and `<->` (distance) operators for nearest-driver queries.
- **Staff insight**: For global scale, use **H3 hexagonal indexing** (Uber's open-source library) instead of PostGIS. H3 provides uniform cell sizes, efficient neighbor queries, and works with any database. Store H3 index in a simple VARCHAR column.

### Ride State Machine
- **Valid transitions**: `requested → matched → arrived → in_progress → completed`. Any state can transition to `cancelled`.
- **Staff insight**: Enforce state transitions at the application level with a state machine library. Use database triggers as a safety net: `CHECK (status IN (...))` and prevent invalid transitions.

### Fare Immutability
- **Snapshot at request**: Store `surge_multiplier`, `base_fare`, and fare breakdown at ride request time.
- **Staff insight**: Never recalculate fare from current surge pricing. The fare is a contract between rider and driver at request time. Store the full breakdown for transparency and dispute resolution.

### Driver Location Tracking
- **Periodic updates**: Driver app sends location every 5 seconds during active rides.
- **Staff insight**: Don't store every location point in PostgreSQL — it's too much write volume. Use a time-series database (InfluxDB) or write to Kafka and aggregate. Store only key points (pickup, dropoff, route changes) in PostgreSQL.

### Surge Pricing Calculation
- **Real-time ratio**: `surge_multiplier = f(demand_count / supply_count)` per zone.
- **Staff insight**: Calculate surge in a separate service that reads rider request rate and driver availability per H3 cell. Use a smoothing algorithm (exponential moving average) to prevent surge oscillation. Publish surge to Redis for low-latency reads.
