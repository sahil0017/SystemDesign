# URL Shortener - Architecture

## System Components

1. **API Gateway**: Entry point; authentication, rate limiting, request routing
2. **URL Service**: Core URL shortening and expansion logic
3. **Redirect Service**: High-performance redirect handling with caching
4. **Analytics Service**: Click tracking, referrer analysis, geographic data
5. **User Service**: User management, authentication, URL ownership
6. **QR Code Service**: QR code generation for short URLs
7. **Database (PostgreSQL)**: URL mappings, user data, analytics aggregation
8. **Cache (Redis)**: Hot URL cache for redirects, click counters, rate limiting
9. **Message Queue (Kafka)**: Analytics events for async processing

## Architecture Diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    CDN (CloudFront)                  │
                    │         Static assets + redirect cache               │
                    └─────────────────────────────────────────────────────┘
                                              │
                                              ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                   API Gateway                        │
                    │         Auth, Rate Limiting, Request Routing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┬─────────────┐
        ▼             ▼              ▼               ▼              ▼             ▼
   ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
   │   URL  │  │ Redirect │  │Analytics │  │   User   │  │    QR    │  │  Auth  │
   │Service │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │Service │
   └────┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬───┘
        │            │             │              │              │             │
        └────────────┴─────────────┴──────────────┴──────────────┴─────────────┘
                                              │
                    ┌─────────────────────────────────────────────────────┐
                    │                 Message Queue (Kafka)                │
                    │         Analytics events for async processing         │
                    └─────────────────────────────────────────────────────┘
                                              │
        ┌─────────────┬──────────────┬───────┴───────┬──────────────┐
        ▼             ▼              ▼               ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │PostgreSQL│  │   Redis  │  │Analytics │  │  Storage  │
   │(URLs,    │  │(Cache,   │  │ DB       │  │(S3 for    │
   │ Users)   │  │ Counters)│  │(Clicks)  │  │ exports)  │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

## Data Flow

### 1. URL Shortening Flow
- Client sends long URL → URL Service
- URL Service validates URL format and accessibility
- Generate short code: Base62 encoding of auto-increment ID or random hash
- If custom alias: check availability with atomic Redis SETNX
- Store mapping in PostgreSQL (short_code → long_url, user_id, expiry)
- Cache in Redis with TTL matching URL expiry
- Return short URL to client

### 2. Redirect Flow (Optimized for Performance)
- Client accesses `/abc123` → Redirect Service
- **Cache check**: Look up short_code in Redis (O(1) operation)
- **Cache hit**: Return 301 redirect with long URL (<1ms)
- **Cache miss**: Query PostgreSQL → cache result → return redirect
- **Analytics**: Publish click event to Kafka for async processing
- **Rate limit**: Check per-IP rate limit in Redis before redirect

### 3. Analytics Flow
- Click event published to Kafka topic `url.clicks`
- Analytics Service consumes events asynchronously
- Aggregate by: short_code, hour, referrer, country, browser, OS
- Store aggregated data in time-series database or PostgreSQL
- Real-time counters updated in Redis for fast reads
- Daily aggregation job compiles hourly data into daily summaries

## Staff-Level Design Considerations

### Short Code Generation
- **Base62 encoding**: 0-9, a-z, A-Z = 62 characters; 6 chars = 56B+ unique codes
- **Auto-increment**: Use distributed ID generator (Snowflake) for sequential IDs
- **Random hash**: Less predictable but requires collision check
- **Staff insight**: Use **Base62 + Snowflake ID** for predictable, collision-free codes with no lookup needed

### Redirect Performance
- **Redis cache**: Hot URLs cached with TTL; <1ms lookup
- **CDN caching**: 301 redirects cached at edge for 1 hour
- **Database optimization**: Single-column index on short_code for O(log n) lookup
- **Staff insight**: At 10M+ redirects/day, **99% should hit Redis cache**. Database is fallback only.

### Analytics at Scale
- **Async processing**: Click events processed asynchronously via Kafka
- **Aggregation**: Hourly aggregation to avoid per-click DB writes
- **Sampling**: For high-traffic URLs, sample 10% of clicks for detailed analytics
- **Staff insight**: Never write analytics on the redirect hot path. Use **async event processing** to keep redirect latency <5ms.

### URL Expiry
- **TTL-based**: Redis cache expires with URL; DB cleanup job removes expired URLs
- **Lazy deletion**: Mark as expired in DB; physical deletion in batch job
- **Staff insight**: Use **Redis TTL** for fast expiry check; **batch job** for DB cleanup to avoid per-request overhead
