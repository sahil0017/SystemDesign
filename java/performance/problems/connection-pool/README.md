# Connection Pool Design

## Problem Statement

Design a connection pool that manages a fixed set of reusable connections (database, HTTP, etc.) to eliminate the overhead of creating and destroying connections for each request.

**Reference**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/)

## Requirements

### Functional Requirements
- **Borrow/Return**: Acquire a connection from the pool and return it when done.
- **Pool sizing**: Configurable minimum and maximum pool size.
- **Connection validation**: Test connection health before handing it out.
- **Timeout**: Block with timeout when no connection is available.
- **Lifecycle management**: Create, validate, and destroy connections.

### Non-Functional Requirements
- **Thread safety**: Multiple threads can borrow/return connections concurrently.
- **Performance**: Minimal overhead on borrow/return operations.
- **Reliability**: Detect and remove broken connections automatically.

## Key Design Decisions
- **Blocking queue**: Use `ArrayBlockingQueue` or `LinkedBlockingQueue` for available connections.
- **Lazy creation**: Create connections on demand up to max pool size.
- **Validation query**: Run a lightweight query (e.g., `SELECT 1`) to test connection health.
- **Idle timeout**: Close connections that have been idle longer than configured timeout.

## Staff-Level Design Considerations

### Pool Sizing Strategy
- **Minimum size**: Pre-create connections at startup to avoid cold-start latency.
- **Maximum size**: Based on downstream capacity (e.g., DB max connections) and application throughput needs.
- **Formula**: `poolSize = CPU_cores * (1 + wait_time/compute_time)` for IO-bound workloads.
- **Staff insight**: Don't set pool size too high. If the downstream service (DB) has a max connection limit, exceeding it causes connection failures. Coordinate pool sizes across all services that share the same downstream resource.

### Connection Validation
- **Test on borrow**: Validate connection before handing it out; adds latency but ensures health.
- **Test on idle**: Validate idle connections periodically; removes broken connections proactively.
- **Test on return**: Validate before returning to pool; prevents broken connections from re-entering.
- **Staff insight**: HikariCP uses "test on idle" with a background thread that validates idle connections every 30 seconds. This is the best balance between latency and reliability.

### HikariCP Best Practices
- **Connection timeout**: Max time to wait for a connection from the pool (default 30s).
- **Idle timeout**: Max idle time before closing a connection (default 10 min).
- **Max lifetime**: Max connection age; prevents stale connections (default 30 min).
- **Leak detection**: Log warning if connection is not returned within threshold (default 0 = disabled).
- **Staff insight**: Always set `maxLifetime` to 30-60 minutes. Database servers close idle connections, and using a stale connection causes errors. Setting maxLifetime slightly shorter than the DB's timeout prevents this.

### Common Pitfalls
- **Connection leak**: Borrowed connection not returned; pool exhausts. Use try-with-resources.
- **Pool too small**: Threads block waiting for connections; high latency.
- **Pool too large**: Exceeds downstream capacity; connection failures.
- **Staff insight**: The most common connection pool bug is connection leaks. Always use try-with-resources or ensure connections are returned in a finally block. Enable leak detection in production to catch leaks early.
