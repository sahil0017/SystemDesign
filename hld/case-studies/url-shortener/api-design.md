# URL Shortener - API Design

## API Overview

RESTful API with JSON responses. All endpoints except redirect require authentication via Bearer token. Redirect endpoint is public and optimized for low latency.

## Endpoints

### Create Short URL

```
POST /api/v1/urls
Content-Type: application/json
Authorization: Bearer <token>

{
    "longUrl": "https://example.com/very/long/url",
    "customAlias": "optional",
    "expiresIn": "24h"
}

Response: 201 Created
{
    "shortUrl": "https://short.url/abc123",
    "shortCode": "abc123",
    "createdAt": "2024-01-01T00:00:00Z",
    "expiresAt": "2024-01-02T00:00:00Z"
}
```

### Redirect Short URL

```
GET /abc123
Response: 301 Moved Permanently
Location: https://example.com/very/long/url
```

### Get URL Analytics

```
GET /api/v1/urls/{shortCode}/analytics
Authorization: Bearer <token>
Response: 200 OK
{
    "shortCode": "abc123",
    "clicks": 150,
    "referrers": {...},
    "countries": {...},
    "browsers": {...}
}
```

### Delete URL

```
DELETE /api/v1/urls/{shortCode}
Authorization: Bearer <token>
Response: 204 No Content
```

## Additional Endpoints

### Get URL Details

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/urls/{shortCode}` | Get URL details (owner only) |
| GET | `/api/v1/urls` | List user's URLs (paginated) |
| PUT | `/api/v1/urls/{shortCode}` | Update URL (expiry, custom alias) |

### Bulk Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/urls/bulk` | Create multiple short URLs (max 100) |
| DELETE | `/api/v1/urls/bulk` | Delete multiple URLs (max 100) |

### QR Code

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/urls/{shortCode}/qr` | Generate QR code for short URL |

## Staff-Level API Design Considerations

### Redirect Optimization
- **301 vs 302**: Use 301 (permanent) for browser caching; 302 (temporary) for analytics tracking
- **Cache headers**: `Cache-Control: public, max-age=3600` for redirect responses
- **Staff insight**: At scale, **90%+ of traffic is redirects**. Optimize redirect path to <1ms by using Redis cache + CDN.

### Rate Limiting
- **Redirect**: 1000 req/min per IP (prevent abuse)
- **Create**: 100 req/min per user
- **Analytics**: 30 req/min per user
- **Staff insight**: Use **token bucket** in Redis for distributed rate limiting

### Custom Alias Validation
- **Length**: 4-50 characters
- **Characters**: Alphanumeric, hyphens, underscores only
- **Reserved words**: Block offensive/profane words using blocklist
- **Uniqueness**: Check availability before creation with atomic Redis SETNX
