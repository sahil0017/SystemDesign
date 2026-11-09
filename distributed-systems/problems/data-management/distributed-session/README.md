# Distributed Session Management

## Problem Statement

Design a distributed session management system that maintains user session state across multiple service instances in a load-balanced environment. The system must support session replication, sticky sessions as fallback, session timeout, and secure session handling for web and mobile applications.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Session creation**: Generate unique session ID on user login; store session data centrally.
- **Session retrieval**: Any service instance can retrieve any user's session.
- **Session timeout**: Configurable idle and absolute timeout with automatic cleanup.
- **Session invalidation**: Logout invalidates session across all instances immediately.
- **Session data**: Store user ID, roles, preferences, cart state, and custom attributes.
- **Token-based**: Support JWT stateless sessions and server-side stateful sessions.

### Non-Functional Requirements
- **Low latency**: Session lookup adds < 5ms to request processing.
- **Scalability**: Handle 10M+ active sessions across service instances.
- **High availability**: Session store available 99.99% of the time.
- **Security**: Session IDs are unguessable; sessions are encrypted in transit.

## Key Design Decisions
- **Redis Cluster**: Primary session store with replication and automatic failover.
- **JWT fallback**: Stateless JWT tokens as backup when Redis is unavailable.
- **Session TTL**: Auto-expire sessions in Redis to prevent memory bloat.
- **Cookie-based**: Session ID stored in HttpOnly, Secure, SameSite cookie.

## Architecture

```
Client (Browser)
   |
   |-- Cookie: session_id --> Load Balancer --> Service Instance A
   |                                              |
   |                                              v
   |                                        Redis Cluster (Session Store)
   |                                              ^
   |                                        Service Instance B
   |                                              ^
   |                                        Service Instance C
```

## Staff-Level Design Considerations

### Stateful vs Stateless Sessions
- **Stateful (server-side)**: Session data in Redis; cookie contains only session ID. More secure, supports invalidation.
- **Stateless (JWT)**: All data in signed JWT token; no server-side lookup needed. No invalidation until expiry.
- **Staff insight**: Use **stateful sessions for sensitive operations** (banking, admin) where immediate invalidation is required. Use **JWT for public APIs** where simplicity and no server-side state matter. Hybrid approach: stateful for web, JWT for mobile/API.

### Redis Session Design
- **Key structure**: `session:{session_id}` → Hash with user_id, roles, data, created_at, last_accessed.
- **TTL management**: Set TTL on session creation; refresh on each access (sliding expiry).
- **Staff insight**: Use **Redis Hash** for session data, not a serialized JSON string. Hash allows partial updates (e.g., update cart without rewriting entire session). Set TTL slightly longer than session timeout to account for clock skew.

### Session Security
- **HttpOnly cookie**: Prevents JavaScript access to session ID (XSS protection).
- **Secure flag**: Cookie sent only over HTTPS.
- **SameSite**: Prevents CSRF — `SameSite=Strict` or `SameSite=Lax`.
- **Staff insight**: Use **SameSite=Lax** for best UX — prevents CSRF while allowing navigation from external links. `SameSite=Strict` breaks login flows from email links. Always regenerate session ID on login to prevent session fixation attacks.

### Session Cleanup
- **Redis TTL**: Automatic expiration when TTL reaches zero.
- **Lazy cleanup**: Redis lazily evicts expired keys; no background thread needed.
- **Staff insight**: Redis TTL is **lazy** — expired keys are deleted on next access, not at exact expiry time. For 10M sessions, this is fine. If you need exact cleanup (e.g., audit logging), use Redis Keyspace Notifications to listen for `expired` events.

### Scaling Session Store
- **Redis Cluster**: Slot-based partitioning distributes sessions across nodes.
- **Memory calculation**: 10M sessions × 1KB/session = 10GB; plan for 2x with replication.
- **Staff insight**: Keep session data **minimal** — store only user_id and essential data. If you need large session data (e.g., full cart), store reference in session and full data in a separate store. Large sessions increase Redis memory usage and replication bandwidth.
