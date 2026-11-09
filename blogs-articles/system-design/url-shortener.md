# Designing a URL Shortener

## Overview

A URL shortener takes a long URL and generates a short alias that redirects to the original. Services like bit.ly, t.co, and tinyurl.com handle billions of redirects daily with sub-100ms latency.

## Key Design Components

### 1. ID Generation
- **Base62 encoding**: Convert auto-increment ID to base62 string (`[a-zA-Z0-9]`)
- **6-character code** = 62^6 = 56.8 billion unique URLs
- **Distribution**: Use distributed ID generator (Snowflake) for multi-instance deployment

### 2. Storage
- **Key-Value Store**: Redis for hot URLs (frequent access), PostgreSQL for persistence
- **Schema**: `url_id (PK), long_url, short_code, created_at, expires_at, user_id`
- **Indexing**: Index on `short_code` for O(1) lookup

### 3. Redirect Flow
```
Client → DNS → CDN → Load Balancer → Service → DB/Cache → 301/302 Redirect
```
- **301 (Permanent)**: Browser caches the redirect — faster but harder to change
- **302 (Temporary)**: Browser always checks — slower but allows analytics and A/B testing

### 4. Analytics
- **Async tracking**: Log clicks asynchronously to avoid blocking redirect
- **Metrics**: Click count, geographic distribution, referrer, device type, time series
- **Storage**: Time-series database (InfluxDB) or columnar store (ClickHouse) for analytics

## Scalability Considerations

### Caching Strategy
- **Redis cache**: Store frequently accessed URLs with TTL
- **CDN caching**: Cache 301 redirects at edge for global performance
- **Cache-aside pattern**: Check cache first, fall back to database

### Handling Viral URLs
- **Hot key problem**: Single URL getting millions of requests
- **Solution**: Multi-level caching — local cache → Redis → CDN → database
- **Rate limiting**: Protect backend from viral URL traffic spikes

## Staff-Level Insights

### Custom Short Codes
- Allow users to specify custom aliases (`bit.ly/my-brand`)
- Handle collisions with reservation system and conflict resolution
- Validate custom codes against reserved words and inappropriate content

### Expiration and Cleanup
- Set TTL on short URLs for temporary use cases
- Use **lazy deletion** — mark as expired, physically delete in batch jobs
- Archive analytics data before deleting expired URLs

### Security Considerations
- **SSRF protection**: Validate long URLs don't point to internal services
- **Phishing prevention**: Show destination preview before redirect
- **Malware scanning**: Scan destination URLs for known threats
