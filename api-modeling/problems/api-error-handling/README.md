# API Error Handling

## Problem Statement

Design a consistent API error handling strategy following RFC 7807 Problem Detail format with proper HTTP status codes, error codes, and retry guidance.

**Reference**: Educative.io, ByteByteGo

## Error Format (RFC 7807)

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "instance": "/api/v1/orders",
  "errors": [
    { "field": "email", "message": "Invalid email format" }
  ]
}
```

## Status Code Guide

| Code | Meaning | Retry? |
|------|---------|--------|
| 400 | Bad Request | No — fix request |
| 401 | Unauthorized | No — re-authenticate |
| 403 | Forbidden | No — insufficient permissions |
| 404 | Not Found | No — resource doesn't exist |
| 409 | Conflict | No — resolve conflict |
| 422 | Unprocessable Entity | No — fix validation |
| 429 | Too Many Requests | Yes — wait Retry-After |
| 500 | Internal Server Error | Yes — server issue |
| 502 | Bad Gateway | Yes — upstream issue |
| 503 | Service Unavailable | Yes — temporary |

## Staff-Level Insight

> "4xx errors are client errors (don't retry). 5xx errors are server errors (retry with backoff)."

- **Staff insight**: Always return **RFC 7807 format** for consistency. Include `retryable: true/false` in error metadata. For 5xx errors, return `Retry-After` header. Never expose internal error details (stack traces) in production — log them server-side, return generic message to client.
