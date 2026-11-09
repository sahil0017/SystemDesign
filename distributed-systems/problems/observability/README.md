# Observability

Systems for monitoring, tracing, and collecting metrics from distributed microservices. Enables debugging production issues, tracking service health, and understanding request flow across services.

## Problems (2)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Distributed Tracing](distributed-tracing/) | Track requests across microservices like Jaeger/OpenTelemetry | Context propagation, sampling, span collection, tiered storage |
| [Distributed Metrics](distributed-metrics/) | Collect and visualize time-series metrics like Prometheus | TSDB, cardinality, downsampling, alerting, aggregation |

## When to Use

- **Distributed Tracing**: When you need to debug latency issues, understand service dependencies, or track a single request across 10+ microservices (e.g., e-commerce checkout flow, API gateway to backend).
- **Distributed Metrics**: When you need real-time dashboards, SLO-driven alerting, or capacity planning based on historical trends (e.g., CPU/memory usage, request rates, error rates, business KPIs).

## Cross-References

- **Topics**: [Kafka](../../kafka/) for metrics/traces transport, [Redis](../../redis/) for real-time aggregation
- **Related**: [Circuit Breaker](../resilience/circuit-breaker/) exposes metrics that feed into the monitoring system. Together with logs, these form the **three pillars of observability** (see [tradeoffs/observability-strategies](../../../tradeoffs/observability-strategies/)).
