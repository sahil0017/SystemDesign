# Horizontal vs Vertical Scaling

## Trade-off Overview

Vertical scaling (scale-up) adds more resources to a single machine. Horizontal scaling (scale-out) adds more machines to a pool.

## Vertical Scaling
- **Pros**: Simple, no code changes, no distributed complexity.
- **Cons**: Hardware limits, single point of failure, expensive at scale.
- **Use when**: Small systems, databases that can't be sharded.

## Horizontal Scaling
- **Pros**: Unlimited scale, fault tolerance, cost-effective commodity hardware.
- **Cons**: Distributed complexity, data partitioning, consistency challenges.
- **Use when**: High traffic, high availability requirements, cloud-native.

## Staff-Level Insight

> "Scale vertically until you can't, then scale horizontally."

- **Staff insight**: Start with **vertical scaling** — it's free complexity. A single PostgreSQL instance on a large machine handles most workloads. Move to **horizontal scaling** when you hit hardware limits or need zero-downtime deployments. Use **load balancer + stateless services** for easy horizontal scaling. For databases, use **read replicas** first, then **sharding** only when necessary.
