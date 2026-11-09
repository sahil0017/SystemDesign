# Data Management

Distributed systems for storing, caching, and managing state across multiple nodes. Covers caching strategies, configuration distribution, and session state management.

## Problems (3)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Distributed Cache](distributed-cache/) | Redis Cluster-like system with partitioning and replication | Hash slots, replication, failover, eviction, persistence |
| [Distributed Config](distributed-config/) | Consul/Etcd-like config management for microservices | Long-polling, local cache, secrets, versioning, environment overrides |
| [Distributed Session](distributed-session/) | Session state across load-balanced service instances | Redis sessions, JWT, sticky sessions, security, scaling |

## When to Use

- **Distributed Cache**: When read-heavy workloads need sub-millisecond access to frequently accessed data (e.g., product catalog, user profiles, API response caching).
- **Distributed Config**: When microservices need runtime config updates without restart (e.g., feature flags, database connection strings, rate limit thresholds).
- **Distributed Session**: When web/mobile apps need to maintain user state across horizontally scaled backend instances (e.g., login sessions, shopping carts).

## Cross-References

- **Topics**: [Redis](../../redis/), [Consistency Models](../../consistency-models/)
- **Related**: [Distributed Rate Limiter](../resilience/distributed-rate-limiter/) often uses the same cache infrastructure for counters.
