# API Security Fundamentals

## Authentication

### OAuth 2.0 / OIDC (Recommended for most APIs)
```
Client → Authorization Server → Access Token (JWT)
Client → API with Bearer Token → Resource Server validates JWT
```
- **Authorization Code Flow**: For web/mobile apps with backend
- **PKCE**: Required for public clients (SPAs, mobile)
- **JWT tokens**: Self-contained, signed, no server-side session lookup

### API Keys (Simple internal services)
```
GET /api/v1/users
X-API-Key: abc123def456
```
- **Pros**: Simple to implement, stateless
- **Cons**: No expiration by default, no fine-grained scopes

### Basic Authentication
- **Only use over HTTPS**
- Base64 encoding is NOT encryption
- Suitable for internal services, not public APIs

## Authorization

### Role-Based Access Control (RBAC)
```
User → Role → Permission → Resource
admin → can_delete → /users/*
viewer → can_read → /users/*
```

### Attribute-Based Access Control (ABAC)
```
Allow if: user.department == resource.department AND action == "read"
```
- More flexible than RBAC
- Evaluates context (time, location, resource attributes)

### JWT Claims for Authorization
```json
{
  "sub": "user-123",
  "roles": ["admin", "editor"],
  "scopes": ["read:users", "write:posts"],
  "org_id": "org-456"
}
```

## Transport Security

### HTTPS/TLS
- **Always use HTTPS** — no exceptions
- **TLS 1.2+** — disable TLS 1.0 and 1.1
- **HSTS Header**: `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### Certificate Management
- Use **Let's Encrypt** for automatic renewal
- Monitor certificate expiration with alerts
- Use **mTLS** for service-to-service communication in microservices

## Input Validation

### Server-Side Validation (Always)
```json
{
  "email": "user@example.com",    // Validate format
  "age": 25,                       // Validate range
  "name": "John"                   // Validate length, sanitize
}
```
- **Never trust client input** — validate on server
- **Whitelist allowed values** for enums
- **Sanitize** to prevent XSS and injection attacks

### Rate Limiting
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```
- **Per-user**: Limit by authenticated user ID
- **Per-IP**: Limit by IP for unauthenticated endpoints
- **Per-endpoint**: Different limits for different operations

## Common Vulnerabilities

### OWASP API Top 10
1. **Broken Object Level Authorization** — Validate ownership of accessed resources
2. **Broken Authentication** — Use strong auth mechanisms, token expiration
3. **Broken Object Property Level Authorization** — Control which fields are returned
4. **Unrestricted Resource Consumption** — Rate limiting, pagination limits
5. **Broken Function Level Authorization** — Enforce role checks on every endpoint
6. **Unrestricted Access to Sensitive Business Flows** — Bot detection, rate limiting
7. **Server Side Request Forgery** — Validate and sanitize URLs
8. **Security Misconfiguration** — Default security headers, disable debug modes
9. **Improper Inventory Management** — Version APIs, decommission old versions
10. **Unsafe Consumption of APIs** — Validate third-party API responses

## CORS (Cross-Origin Resource Sharing)

```
Access-Control-Allow-Origin: https://frontend.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```
- **Never use `*`** in production with credentials
- Whitelist specific origins
- Pre-flight requests (OPTIONS) should be cached

## Staff-Level Insights

### Token Strategy
- **Short-lived access tokens** (15-30 min) + **refresh tokens** (7-30 days)
- Store refresh tokens **httpOnly, secure, sameSite** cookies
- Revoke refresh tokens on suspicious activity

### API Gateway Security
- Centralize authentication at the **gateway level**
- Use **JWT validation** at gateway, pass user context to services
- Implement **request signing** for service-to-service calls

### Secret Management
- Never store secrets in code or environment variables in containers
- Use **HashiCorp Vault**, **AWS Secrets Manager**, or **GCP Secret Manager**
- Rotate secrets automatically on a schedule

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 0
Referrer-Policy: strict-origin-when-cross-origin
```
