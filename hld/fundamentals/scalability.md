# Scalability

## Overview

Scalability is the ability of a system to handle increased load by adding resources while maintaining performance, reliability, and cost-efficiency. For staff-level engineers, scalability is not just about adding capacity — it's about designing systems that scale **predictably**, **gracefully degrade** under load, and provide **observability** into scaling behavior.

## Types of Scaling

### Vertical Scaling (Scale Up)
- Adding more power (CPU, RAM, storage) to a single machine
- **Pros**: Simple, no code changes needed, no distributed system complexity
- **Cons**: Hardware limits (diminishing returns past ~128 cores), single point of failure, downtime during upgrade, cost-inefficient at scale
- **When to use**: Databases with complex queries (OLAP), legacy monoliths, memory-intensive workloads
- **Staff insight**: Vertical scaling has hard limits — AWS EC2 instances top out at ~448 vCPUs. Plan for horizontal scaling from day one.

### Horizontal Scaling (Scale Out)
- Adding more machines to the pool
- **Pros**: No theoretical limit, fault tolerance, zero-downtime deployments, cost-efficient
- **Cons**: Requires stateless design, data consistency challenges, operational complexity, network overhead
- **When to use**: Web services, APIs, microservices, stateless workers
- **Staff insight**: Horizontal scaling introduces distributed system problems (consistency, partial failures, network partitions). Complexity grows non-linearly with scale.

## Key Metrics

| Metric | Definition | Target | Tool |
|--------|-----------|--------|------|
| **Throughput** | Requests per second (RPS) / ops/sec | Define SLA per service | Prometheus, Datadog |
| **Latency** | p50/p95/p99 response time | p99 < SLA threshold | Histograms, p99 tracking |
| **Concurrency** | Simultaneous active connections | Connection pool sizing | APM tools |
| **Utilization** | CPU, memory, disk I/O, network | 60-70% avg, <90% peak | CloudWatch, cAdvisor |
| **Error Rate** | 4xx/5xx percentage | <0.1% for p99 | Sentry, PagerDuty |
| **Saturation** | Queue depth, thread pool usage | <80% saturation | Custom metrics |

### Staff-Level Metric Philosophy
- **Track percentiles, not averages**: p99 latency reveals tail latency problems that averages hide
- **Use the USE method** (Utilization, Saturation, Errors) for resource monitoring
- **Apply RED method** (Rate, Errors, Duration) for service monitoring
- **Capacity planning**: Use 90th-percentile traffic + 2x headroom for provisioning

## Scaling Strategies

### 1. Stateless Services
- **Design**: Externalize all state to databases, caches, or session stores
- **Implementation**: Use tokens/JWT instead of server-side sessions; store uploads in object storage (S3)
- **Staff insight**: True statelessness is rare — even "stateless" services have connection pools, caches, and rate limiters. Design for **graceful rebalancing** when instances scale in/out.

### 2. Load Balancing
- **Layer 4 (Transport)**: TCP/UDP load balancing — fast, simple, no SSL termination
- **Layer 7 (Application)**: HTTP load balancing — path-based routing, header inspection, SSL termination
- **Staff insight**: At scale, the load balancer itself becomes a bottleneck. Use anycast DNS + multiple LBs behind a global traffic manager (e.g., AWS Global Accelerator, Cloudflare Load Balancer).

### 3. Database Scaling
- **Read Replicas**: Scale reads; lag-aware routing for consistency-sensitive reads
- **Sharding**: Horizontal partition by user ID, tenant, or geographic region
- **Polyglot Persistence**: Use the right database for each workload (SQL for transactions, NoSQL for reads, time-series for metrics)
- **Staff insight**: Database scaling is the hardest part of system scaling. Invest in **schema design** and **query optimization** before adding infrastructure.

### 4. Caching
- **Multi-tier caching**: Browser → CDN → Application cache → Database
- **Cache strategies**: Cache-aside (lazy), write-through, write-behind (async)
- **Staff insight**: Cache invalidation is one of the hardest problems in computer science. Use **TTL + event-driven invalidation** for critical data. Monitor cache hit rates — <80% indicates a design problem.

### 5. Content Delivery Networks (CDN)
- **Static assets**: Images, CSS, JS, fonts served from edge locations
- **Dynamic acceleration**: Origin shield, connection multiplexing, route optimization
- **Staff insight**: At global scale, use **edge computing** (Cloudflare Workers, AWS Lambda@Edge) to push logic closer to users, reducing origin load by 90%+.

### 6. Microservices & Bounded Contexts
- **Decomposition**: Split by domain/bounded context, not by technical layer
- **Independent scaling**: Each service scales based on its own load profile
- **Staff insight**: Microservices add operational overhead. Only decompose when you have **independent scaling requirements** or **team autonomy** needs. A well-structured monolith often outperforms premature microservices.

## Common Patterns

### Read Replicas
- **Implementation**: Primary handles writes; replicas handle reads with configurable lag
- **Trade-off**: Replication lag (seconds to minutes) vs read scalability
- **Staff insight**: Use **read-your-writes consistency** by routing post-write reads to the primary. For analytics, use **materialized views** or **CDC pipelines** instead of direct replica reads.

### Caching Layer
- **Tools**: Redis (data structures), Memcached (simple caching), CDN (edge)
- **Patterns**: Cache-aside, write-through, write-behind, refresh-ahead
- **Staff insight**: Implement **cache stampede protection** with mutex/semaphore. Use **stale-while-revalidate** pattern to serve stale data during cache misses while async refresh occurs.

### Message Queues & Async Processing
- **Tools**: Kafka (event streaming), RabbitMQ (task queues), SQS (cloud-native)
- **Patterns**: Event-driven architecture, CQRS, event sourcing
- **Staff insight**: Async processing hides latency but doesn't eliminate it. Track **end-to-end latency** including queue wait time. Use **dead letter queues** for poison messages.

### Auto-scaling
- **Metrics-based**: CPU, memory, RPS, queue depth
- **Predictive**: ML-based scaling based on historical patterns (AWS Predictive Scaling)
- **Staff insight**: Auto-scaling has cold-start latency (30s-5min). Use **proactive scaling** for predictable traffic (e.g., daily peaks). Always set **min/max bounds** to prevent runaway costs.

## Staff-Level Scaling Checklist

1. **Define SLOs first**: What does "scalable" mean for your system? (e.g., p99 < 200ms at 10K RPS)
2. **Load test early**: Use k6, Gatling, or Locust to find bottlenecks before production
3. **Design for failure**: Assume any component can fail at any time
4. **Implement circuit breakers**: Prevent cascade failures under load
5. **Monitor everything**: Metrics, logs, traces — observability is non-negotiable
6. **Capacity plan**: Track growth trends and plan infrastructure 6 months ahead
7. **Cost awareness**: Scaling should be cost-efficient; track $/request and $/user
