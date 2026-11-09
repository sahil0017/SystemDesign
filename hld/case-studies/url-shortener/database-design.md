# URL Shortener - Database Design

## Database Strategy

- **PostgreSQL**: URL mappings, user data, analytics aggregation (ACID)
- **Redis**: Hot URL cache for redirects, click counters, rate limiting
- **Kafka**: Analytics events for async processing

## PostgreSQL Schema

### Users
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### URLs
```sql
CREATE TABLE urls (
    id BIGINT PRIMARY KEY,
    short_code VARCHAR(20) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    click_count BIGINT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_urls_user ON urls(user_id, created_at DESC);
CREATE INDEX idx_urls_expires ON urls(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_urls_active ON urls(short_code) WHERE is_active = TRUE;
```

### Analytics (Aggregated)
```sql
CREATE TABLE analytics_hourly (
    analytics_id BIGINT PRIMARY KEY,
    short_code VARCHAR(20) NOT NULL,
    hour TIMESTAMP NOT NULL,
    click_count INT DEFAULT 0,
    unique_visitors INT DEFAULT 0,
    referrer_counts JSONB, -- {"google.com": 50, "twitter.com": 30}
    country_counts JSONB, -- {"US": 60, "UK": 20}
    browser_counts JSONB, -- {"Chrome": 70, "Safari": 20}
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (short_code) REFERENCES urls(short_code)
);

CREATE INDEX idx_analytics_code_hour ON analytics_hourly(short_code, hour DESC);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `url:{short_code}` | String | Cached long URL for redirect | Matches URL expiry |
| `url:clicks:{short_code}` | String | Real-time click counter | No TTL |
| `rate:{ip}:redirect` | String | Per-IP redirect rate limit | 1min |
| `rate:{user_id}:create` | String | Per-user create rate limit | 1min |
| `alias:{custom_alias}` | String | Custom alias availability check | 10s |

## Indexes Strategy

### PostgreSQL Indexes
- **URL lookup**: Unique index on `short_code` for O(log n) redirect lookup
- **User URLs**: Composite index on `(user_id, created_at DESC)` for listing
- **Expiry cleanup**: Partial index on `expires_at` for batch cleanup job
- **Analytics**: Composite index on `(short_code, hour DESC)` for time-series queries

## Staff-Level Database Considerations

### URL Encoding
- **Base62**: 0-9, a-z, A-Z = 62 characters; 6 chars = 56B+ unique codes
- **Snowflake ID**: Distributed ID generator for sequential, collision-free codes
- **Staff insight**: Use **Base62(Snowflake ID)** — no collision check needed, predictable, no hot spots

### Click Count Management
- **Redis counter**: Increment on each redirect; async batch sync to PostgreSQL every 5min
- **Analytics**: Hourly aggregation from Kafka events; avoid per-click DB writes
- **Staff insight**: Never write click count to DB on every redirect — use **async batch writes**

### URL Expiry
- **Redis TTL**: Cache expires with URL; redirect fails gracefully on cache miss
- **DB cleanup**: Batch job runs every hour to mark expired URLs as inactive
- **Staff insight**: Use **lazy deletion** — mark expired, don't physically delete until batch job
