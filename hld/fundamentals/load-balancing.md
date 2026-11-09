# Load Balancing

## Overview

Load balancing distributes incoming network traffic across multiple servers to ensure no single server becomes a bottleneck. For staff engineers, load balancing is not just about distribution — it's about **resilience**, **observability**, and **intelligent routing** based on real-time system state.

## Types

### Layer 4 (Transport Layer)
- **Protocol**: Operates at TCP/UDP level (OSI Layer 4)
- **Routing**: Forwarding based on IP address and port only
- **Performance**: Faster, lower latency (~1-2μs per decision), no SSL termination overhead
- **Use cases**: TCP proxies, database load balancing, gRPC services, WebSocket connections
- **Staff insight**: L4 load balancers can handle 1M+ connections/sec. Use for internal service-to-service traffic where HTTP inspection is unnecessary.

### Layer 7 (Application Layer)
- **Protocol**: Operates at HTTP/HTTPS level (OSI Layer 7)
- **Routing**: Can inspect headers, cookies, URL paths, query parameters, JWT tokens
- **Features**: SSL termination, compression, request/response rewriting, A/B testing, canary deployments
- **Use cases**: Web applications, API gateways, microservices with path-based routing
- **Staff insight**: L7 adds 5-50ms latency due to packet inspection. Use only when you need content-aware routing. For high-throughput APIs, consider L4 + service mesh.

## Algorithms

### Basic Algorithms

| Algorithm | How It Works | Best For | Limitations |
|-----------|-------------|----------|-------------|
| **Round Robin** | Cycles through servers in order | Uniform capacity, stateless services | Ignores server load |
| **Weighted Round Robin** | Assigns weights based on capacity | Heterogeneous server pools | Static weights don't adapt |
| **Least Connections** | Routes to server with fewest active connections | Variable request duration | Connection count ≠ actual load |
| **Least Response Time** | Routes to server with lowest avg response time | Latency-sensitive services | Cold start bias |
| **IP Hash** | Hash(client IP) → server | Session persistence without state | Uneven distribution with NAT |
| **Random** | Randomly selects a server | Simple workloads | No predictability |
| **Consistent Hashing** | Ring-based hashing with virtual nodes | Cache distribution, sharding | Complex implementation |

### Advanced Algorithms

- **Power of Two Choices**: Pick 2 random servers, route to the less loaded one — near-optimal with minimal overhead
- **Adaptive Load Balancing**: ML-based routing using real-time metrics (latency, error rate, queue depth)
- **Geographic Routing**: Route to nearest region; failover to next closest on health check failure
- **Staff insight**: No single algorithm is best. Use **hybrid approaches**: consistent hashing for cache affinity + least connections for new requests.

## Health Checks

### Active Health Checks
- **Mechanism**: Load balancer periodically sends HTTP/TCP requests to verify server health
- **Configuration**: Interval (5-30s), timeout (2-10s), healthy/unhealthy thresholds
- **Staff insight**: Active checks add load. Use lightweight endpoints (`/healthz`) that check dependencies (DB, cache) without processing business logic.

### Passive Health Checks
- **Mechanism**: Monitor actual server responses for errors (5xx, connection refused, timeouts)
- **Configuration**: Error threshold, evaluation window, ejection duration
- **Staff insight**: Passive checks detect real problems but react slower. Combine with active checks for fast detection + real-world validation.

### Circuit Breaker Integration
- **Pattern**: When error rate exceeds threshold, stop routing to unhealthy backend
- **Recovery**: Gradual reintroduction with canary traffic (1% → 10% → 100%)
- **Staff insight**: Implement **half-open state** — send probe requests to recovering backends before full traffic restoration.

## Session Persistence (Sticky Sessions)

| Method | How It Works | Trade-offs |
|--------|-------------|------------|
| **IP-based** | Hash client IP to same backend | Breaks with NAT/CNAT |
| **Cookie-based** | Insert routing cookie in response | Cookie overhead, privacy concerns |
| **Header-based** | Route by custom header (e.g., X-Session-ID) | Requires client cooperation |
| **Stateless alternative** | Use distributed session store (Redis) | Adds latency, but enables true horizontal scaling |

- **Staff insight**: Avoid sticky sessions when possible. Design stateless services and use distributed session stores. Sticky sessions mask architectural problems.

## Global Load Balancing

- **DNS-based**: Route users to nearest region via DNS (AWS Route 53, Cloudflare Load Balancer)
- **Anycast**: Same IP announced from multiple locations; BGP routes to nearest
- **Global Server Load Balancer (GSLB)**: Health-aware multi-region routing with failover
- **Staff insight**: DNS-based routing has TTL caching issues (30s-24h). Use **health-check-driven DNS** with low TTL (30-60s) for fast failover.

## Common Tools

| Tool | Type | Strengths | Use Case |
|------|------|-----------|----------|
| **Nginx** | L4/L7 | Mature, large ecosystem, high performance | Web apps, reverse proxy |
| **HAProxy** | L4/L7 | TCP/HTTP optimization, detailed stats | High-throughput APIs |
| **AWS ALB/NLB** | L4/L7 | Managed, auto-scaling, integration | AWS-native workloads |
| **Envoy** | L4/L7 | Service mesh, observability, extensible | Microservices, Istio |
| **Traefik** | L7 | Auto-discovery, Kubernetes-native | Kubernetes ingress |
| **Cloudflare LB** | L4/L7 | Global anycast, DDoS protection | Global web apps |

## Staff-Level Load Balancing Checklist

1. **Choose L4 vs L7 wisely**: L4 for internal services, L7 for external APIs needing content-aware routing
2. **Implement health checks**: Both active (proactive) and passive (reactive) with appropriate thresholds
3. **Plan for failover**: Multi-AZ deployment with automatic backend removal on health check failure
4. **Monitor LB metrics**: Connection count, request rate, latency, error rate, backend utilization
5. **Set timeouts appropriately**: Connect timeout (5s), read timeout (30s), write timeout (30s)
6. **Enable connection draining**: Gracefully remove backends during deployments (30-60s drain time)
7. **Consider the LB as a bottleneck**: At 100K+ RPS, the LB itself needs scaling or replacement with service mesh
