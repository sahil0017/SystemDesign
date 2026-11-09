# Connection Pooling

## Trade-off Overview

Connection pooling reuses existing database connections instead of creating new ones for each request. Direct connections create a new connection per request.

## Connection Pooling (HikariCP, PgBouncer)
- **Pros**: Reduced latency (no handshake), resource control, connection limit.
- **Cons**: Pool exhaustion risk, stale connections, memory overhead.
- **Use when**: High request rate, limited DB connections, latency-sensitive.

## Direct Connections
- **Pros**: Simple, no pool management, always fresh connection.
- **Cons**: High latency (TCP handshake + auth), DB connection limit exhaustion.
- **Use when**: Low traffic, batch jobs, infrequent queries.

## Staff-Level Insight

> "Always use connection pooling for web applications."

- **Staff insight**: Use **HikariCP** for application-level pooling (fast, lightweight). Use **PgBouncer** for transaction-level pooling when you have thousands of application instances. Set pool size to `num_cores * 2 + disk_spindles` (Jim Wong's formula). Monitor pool wait time — if threads wait for connections, increase pool size or optimize queries.
