# Uber - Database Design

## Database Strategy

- **PostgreSQL + PostGIS**: User data, trips, payments (ACID + geospatial queries)
- **Cassandra**: Location traces, trip history (high write throughput)
- **Redis**: Driver locations, surge multipliers, session data, real-time state
- **Elasticsearch**: Trip search, support queries

## PostgreSQL Schema

### Users (Riders & Drivers)
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(100) NOT NULL,
    profile_picture_url VARCHAR(500),
    user_type VARCHAR(20) NOT NULL, -- 'rider', 'driver', 'both'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE drivers (
    driver_id BIGINT PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    vehicle_year INT,
    license_plate VARCHAR(20),
    vehicle_type VARCHAR(20), -- 'uberX', 'uberXL', 'black'
    is_available BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3,2) DEFAULT 5.00,
    total_trips INT DEFAULT 0,
    document_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_drivers_available ON drivers(is_available, rating DESC);
```

### Trips
```sql
CREATE TABLE trips (
    trip_id BIGINT PRIMARY KEY,
    rider_id BIGINT NOT NULL,
    driver_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'requested', 'matched', 'started', 'completed', 'cancelled'
    pickup_lat DECIMAL(10,8) NOT NULL,
    pickup_lon DECIMAL(11,8) NOT NULL,
    dropoff_lat DECIMAL(10,8) NOT NULL,
    dropoff_lon DECIMAL(11,8) NOT NULL,
    pickup_geo GEOGRAPHY(POINT, 4326),
    dropoff_geo GEOGRAPHY(POINT, 4326),
    estimated_fare DECIMAL(10,2),
    actual_fare DECIMAL(10,2),
    surge_multiplier DECIMAL(3,2) DEFAULT 1.00,
    distance_km DECIMAL(10,2),
    duration_min INT,
    requested_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_by VARCHAR(20), -- 'rider', 'driver', 'system'
    cancellation_reason TEXT,
    FOREIGN KEY (rider_id) REFERENCES users(user_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE INDEX idx_trips_rider ON trips(rider_id, requested_at DESC);
CREATE INDEX idx_trips_driver ON trips(driver_id, requested_at DESC);
CREATE INDEX idx_trips_status ON trips(status, requested_at DESC);
CREATE INDEX idx_trips_pickup_geo ON trips USING GIST (pickup_geo);
```

### Payments
```sql
CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    trip_id BIGINT NOT NULL,
    rider_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'credit_card', 'paypal', 'cash'
    status VARCHAR(20) NOT NULL, -- 'pending', 'completed', 'refunded', 'failed'
    stripe_charge_id VARCHAR(100),
    idempotency_key VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (rider_id) REFERENCES users(user_id)
);

CREATE INDEX idx_payments_trip ON payments(trip_id);
CREATE INDEX idx_payments_rider ON payments(rider_id, created_at DESC);
```

### Ratings
```sql
CREATE TABLE ratings (
    rating_id BIGINT PRIMARY KEY,
    trip_id BIGINT NOT NULL,
    rater_id BIGINT NOT NULL,
    ratee_id BIGINT NOT NULL,
    score INT NOT NULL CHECK (score BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (trip_id, rater_id, ratee_id),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);
```

## Cassandra Schema (Location Traces)

### Location Traces
```sql
CREATE TABLE location_traces (
    trip_id BIGINT,
    timestamp TIMESTAMP,
    driver_id BIGINT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    speed DECIMAL(5,2),
    heading DECIMAL(3,1),
    PRIMARY KEY (trip_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp ASC);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `driver:location:{driver_id}` | Geo | Driver GPS coordinates | 30s |
| `driver:status:{driver_id}` | String | Online/offline status | No TTL |
| `surge:{zone_id}` | String | Surge multiplier per S2/H3 zone | 30s |
| `ride:active:{ride_id}` | Hash | Active ride state | 1h |
| `session:{user_id}` | Hash | Session data | 24h |
| `rate:{user_id}:{endpoint}` | String | Rate limit counter | 1min |
| `driver:nearby:{zone_id}` | Set | Available drivers in zone | 10s |

## Indexes Strategy

### PostgreSQL Indexes
- **Geospatial**: GIST index on pickup/dropoff coordinates for nearest-driver queries
- **Trip history**: Composite index on `(rider_id, requested_at DESC)`
- **Driver availability**: Partial index `WHERE is_available = TRUE`
- **Payment lookup**: Unique index on `idempotency_key`

### Cassandra Partition Strategy
- **Partition key**: `trip_id` for location traces (all trace points for a trip)
- **Clustering key**: `timestamp ASC` for chronological ordering
- **Compaction**: SizeTieredCompaction for time-series data

## Staff-Level Database Considerations

### Geospatial Queries
- **PostGIS**: `ST_DWithin` for radius-based driver search
- **S2/H3**: Hierarchical cells for zone-based surge pricing
- **Redis Geo**: `GEORADIUS` for quick nearest-driver lookup

### Trip State Machine
- States: `requested → matched → started → completed` or `→ cancelled`
- Use **database constraints** to enforce valid state transitions
- **Optimistic locking** with version column for concurrent updates

### Payment Idempotency
- **Idempotency key**: Client-generated UUID per payment attempt
- **Unique constraint**: On `idempotency_key` column
- **Return cached result**: If key exists, return original payment result
