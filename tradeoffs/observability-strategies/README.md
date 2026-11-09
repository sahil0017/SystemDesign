# Observability Strategies

## Problem Statement

Design an observability strategy for a distributed microservices architecture. The system must provide visibility into service health, request flow, performance metrics, and error rates. Choose between monitoring, logging, and tracing approaches, and determine how to correlate data across services for effective debugging and incident response.

**Reference**: Educative.io, ByteByteGo, HelloInterview

## Trade-off Options

### Option 1: Metrics-Centric (Prometheus + Grafana)
- **Pros**: Low overhead, excellent for alerting, time-series queries, mature ecosystem.
- **Cons**: Limited debugging context, requires pre-defined metrics, no request-level visibility.

### Option 2: Logs-Centric (ELK Stack / Loki)
- **Pros**: Rich context, searchable, no pre-definition needed, good for debugging.
- **Cons**: High storage cost, slow queries at scale, no real-time alerting without parsing.

### Option 3: Traces-Centric (Jaeger / Zipkin)
- **Pros**: End-to-end request visibility, service dependency mapping, latency breakdown.
- **Cons**: High overhead, sampling loses data, expensive storage for full traces.

### Option 4: Full Stack (Metrics + Logs + Traces)
- **Pros**: Complete visibility, correlated data, best debugging experience.
- **Cons**: Highest cost and complexity, requires tool integration, data volume management.

## Decision Framework

| Factor | Metrics | Logs | Traces | Full Stack |
|--------|---------|------|--------|------------|
| Overhead | Low (<1%) | Medium | High (5-10%) | High |
| Debugging | Limited | Good | Excellent | Best |
| Alerting | Excellent | Poor | Medium | Excellent |
| Cost | Low | Medium | High | Highest |
| Setup complexity | Low | Medium | High | Highest |

## Key Design Decisions

### The Three Pillars of Observability
1. **Metrics**: Numerical data over time (CPU, memory, request rate, error rate, latency percentiles)
2. **Logs**: Timestamped events with context (error messages, audit trails, debug info)
3. **Traces**: Request flow across services (span timing, dependencies, errors)

### Correlation Strategy
- **Trace ID propagation**: Pass trace ID through all services and include in logs
- **Structured logging**: JSON logs with trace ID, span ID, service name, and level
- **Dashboard integration**: Click from metric alert → trace → correlated logs

### Data Retention
- **Metrics**: Raw data 30 days, downsampled 1 year
- **Logs**: Hot storage 7 days, warm storage 30 days, cold storage 1 year
- **Traces**: Error traces retained, sampled traces 7 days

## Staff-Level Insights

### Observability vs Monitoring
- **Monitoring**: Tells you **when** something is wrong (alerts, dashboards)
- **Observability**: Tells you **why** something is wrong (queries, exploration)
- **Staff insight**: Don't confuse the two. Monitoring is reactive (pre-defined alerts); observability is proactive (ability to ask new questions). Invest in both — monitoring for on-call, observability for debugging.

### SLO-Driven Alerting
- **Error budget**: Define SLO (e.g., 99.9% availability); alert when budget burn rate is too high
- **Multi-window alerting**: Fast alert for short-term burn, slow alert for long-term trend
- **Staff insight**: Alert on **SLO burn rate**, not raw metrics. If your SLO is 99.9% availability, you have 43.8 minutes of downtime per month. Alert when you're burning that budget too fast, not when CPU is high. This reduces alert fatigue and focuses on what matters to users.

### Log Volume Management
- **Structured logging**: JSON format with consistent fields for efficient parsing
- **Log levels**: Use DEBUG sparingly in production; INFO for business events; WARN/ERROR for issues
- **Sampling**: Sample debug logs in high-traffic services to control volume
- **Staff insight**: Logs are the **most expensive** pillar. A single high-traffic service can generate terabytes per day. Use **log sampling** — keep all ERROR/WARN logs, but sample INFO/DEBUG at 1-10%. Tools like Loki with label-based indexing are cheaper than ELK for large-scale log storage.

### Distributed Tracing Best Practices
- **Context propagation**: Ensure trace context flows through HTTP, gRPC, message queues, and databases
- **Sampling strategy**: Head-based for cost control, tail-based for error retention
- **Span design**: Create spans for meaningful operations, not every method call
- **Staff insight**: **Don't trace everything**. Trace at service boundaries and for expensive operations (DB calls, external APIs). Too many spans create noise and overhead. Use **semantic conventions** (OpenTelemetry) so spans are consistent across services and queryable.
