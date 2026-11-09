# Distributed Session Store Database Schema Design

## Problem Statement

Design a NoSQL schema for a distributed session store that handles millions of concurrent user sessions. Store session data (user_id, preferences, cart items, auth tokens) with TTL-based expiration and fast lookup. Support horizontal scaling via clustering, session replication for failover, and secure session management.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Session Creation**: Generate unique session ID, store user data and metadata.
- **Session Data**: User ID, auth token, preferences, cart items, last activity.
- **TTL Expiration**: Auto-expire inactive sessions after configurable timeout.
- **Session Refresh**: Extend TTL on each user activity.
- **Session Invalidiation**: Logout, password change, security event.
- **Session Migration**: Move session between app servers during deployment.

### Non-Functional Requirements
- **Read latency**: < 5ms for session lookup (p99).
- **Write latency**: < 10ms for session update (p99).
- **Scalability**: 10M+ concurrent sessions across cluster.
- **Availability**: 99.99% uptime; no single point of failure.
- **Security**: Session fixation prevention, secure token generation.

## Key Design Decisions

- **Redis as primary store**: In-memory key-value with persistence options.
- **Session ID as key**: Random 256-bit token as session key.
- **Hash structure**: Session data stored as Redis Hash for field-level updates.
- **TTL for expiration**: Automatic session expiry via Redis TTL.
- **Cluster mode**: Horizontal scaling via slot-based partitioning.

## Schema Design (Redis)

### Session Data Structure

```
# Session key pattern
Key:    session:{session_id}
Type:   Hash
TTL:    Configurable (default 30 minutes)
Fields:
  - user_id: "12345"
  - auth_token: "eyJhbGciOiJIUzI1NiIs..."
  - username: "john_doe"
  - role: "admin"
  - preferences: "{\"theme\":\"dark\",\"lang\":\"en\"}"
  - cart_items: "[{\"id\":\"p1\",\"qty\":2},{\"id\":\"p3\",\"qty\":1}]"
  - last_activity: "1705420800"
  - ip_address: "192.168.1.1"
  - user_agent: "Mozilla/5.0 ..."
  - created_at: "1705418000"
```

### Session Index (for user → session mapping)

```
# User's active session
Key:    user:session:{user_id}
Type:   String
Value:  {session_id}
TTL:    Same as session TTL

# Use for: invalidate all sessions for a user on password change
```

### Session Lock (for concurrent access)

```
# Distributed lock per session
Key:    session:lock:{session_id}
Type:   String
Value:  {request_id}
TTL:    5 seconds

# Use for: prevent concurrent cart updates
```

### Rate Limiting

```
# Per-session rate limit
Key:    rate:session:{session_id}:{endpoint}
Type:   String (counter)
Value:  {count}
TTL:    60 seconds

# Per-IP rate limit
Key:    rate:ip:{ip_address}
Type:   String (counter)
Value:  {count}
TTL:    60 seconds
```

### Session Analytics (aggregated)

```
# Active sessions counter
Key:    stats:active_sessions
Type:   String
Value:  {count}
TTL:    None (updated periodically)

# Sessions created per hour
Key:    stats:sessions_created:{hour_bucket}
Type:   String
Value:  {count}
TTL:    24 hours
```

### Redis Cluster Configuration

```
# Cluster mode with 3 master + 3 replica nodes
# 16384 hash slots distributed across masters
# Replication factor: 1 replica per master
# Persistence: AOF every second + RDB every 15 minutes

redis.conf:
  cluster-enabled yes
  cluster-config-file nodes.conf
  cluster-node-timeout 5000
  appendonly yes
  appendfsync everysec
  save 900 1
  save 300 10
  save 60 10000
```

## Indexes Strategy

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `session:{id}` | Hash | Session data lookup | Configurable |
| `user:session:{user_id}` | String | User → session mapping | Same as session |
| `session:lock:{id}` | String | Concurrent access lock | 5s |
| `rate:session:{id}:{ep}` | String | Per-session rate limit | 60s |
| `rate:ip:{ip}` | String | Per-IP rate limit | 60s |
| `stats:active_sessions` | String | Active session count | None |

## Staff-Level Design Considerations

### Session Affinity vs Stateless
- **No session affinity**: Any app server can handle any request; session is in Redis.
- **Staff insight**: Don't use sticky sessions (session affinity in load balancer). They prevent rolling deployments and cause uneven load. Store sessions in Redis cluster so any app server can serve any request.

### Redis Cluster Partitioning
- **Slot-based**: 16384 hash slots; each master owns a range of slots.
- **Staff insight**: Redis Cluster uses CRC16(session_id) % 16384 to determine the slot. With random session IDs, distribution is uniform. For hot keys (frequently accessed sessions), use key tagging: `session:{user_id}:profile` ensures all profile-related keys go to the same slot via `{user_id}` tag.

### Lazy vs Eager Expiration
- **Lazy**: Redis expires keys on access or during background cleanup.
- **Staff insight**: Redis does NOT guarantee immediate expiration. A session may live slightly past its TTL until Redis's background expiration cycle runs. For security-critical sessions (admin), implement application-level TTL check on every request: `if (now - last_activity > max_age) invalidate()`.

### Session Replication & Failover
- **Master-replica**: Each master has 1 replica; automatic failover on master death.
- **Staff insight**: Redis Sentinel or Cluster handles automatic failover. During failover (~1-5 seconds), writes may be lost if AOF is `everysec`. Use `appendfsync always` for zero data loss at the cost of write throughput. For most session stores, `everysec` is acceptable — losing 1 second of session updates is better than 50% write throughput degradation.

### Security Considerations
- **Session fixation**: Generate new session ID on login; invalidate old session.
- **Staff insight**: On authentication, create a new session with a new random ID and delete the old one. This prevents session fixation attacks. Use cryptographically secure random tokens (256-bit) for session IDs. Never use predictable session IDs (e.g., user_id, timestamp). Store `ip_address` and `user_agent` in the session and validate on each request — invalidate if they change.
