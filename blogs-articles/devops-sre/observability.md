# Observability: The Three Pillars

## Overview

Observability is the ability to understand a system's internal state by examining its outputs. The three pillars — metrics, logs, and traces — provide complementary views of system behavior for effective debugging and monitoring.

## Metrics

### What They Are
Numerical measurements over time, stored in time-series databases.

### Key Types
- **Counters**: Monotonically increasing values (request count, error count)
- **Gauges**: Values that go up and down (CPU usage, memory, queue size)
- **Histograms**: Distribution of values (request latency, response size)

### Best Practices
- Use **percentiles** (P50, P95, P99) for latency, not averages
- Label metrics for filtering (service, endpoint, status code)
- Set **alerting rules** on meaningful thresholds

```prometheus
# Example: P99 latency per endpoint
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

## Logs

### What They Are
Timestamped records of events with context (level, message, metadata).

### Structured Logging
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "ERROR",
  "service": "order-service",
  "trace_id": "abc123",
  "message": "Payment failed",
  "order_id": "ord-456",
  "error": "TimeoutException: payment gateway timeout"
}
```

### Best Practices
- Use **structured logging** (JSON) for efficient parsing and querying
- Include **correlation IDs** (trace ID) for linking logs to traces
- Set appropriate **log levels**: ERROR for failures, WARN for recoverable issues, INFO for business events, DEBUG for troubleshooting

## Traces

### What They Are
End-to-end request flow across services with timing and dependency information.

### Key Concepts
- **Trace**: Complete request journey (unique trace ID)
- **Span**: Single operation within a trace
- **Context propagation**: Pass trace ID across service boundaries

### Best Practices
- Use **OpenTelemetry** for vendor-neutral instrumentation
- Implement **sampling** to control cost (1% head-based + 100% for errors)
- Correlate traces with logs using **trace ID**

## Correlating the Three Pillars

```
Metric Alert: Error rate > 1% on /api/orders
    ↓
Trace Query: Find error traces for /api/orders in last 5 minutes
    ↓
Log Query: Find logs with trace_id = "abc123"
    ↓
Root Cause: Database connection pool exhausted
```

## Staff-Level Insights

### Cost Management
- **Metrics**: Cheapest — time-series data is compact
- **Logs**: Most expensive — text data grows rapidly
- **Traces**: Medium — structured but high volume
- **Staff insight**: Implement **tiered storage** — hot data (7 days) in fast storage, warm data (30 days) in cheaper storage, cold data (90+ days) in archive. A single high-traffic service can generate TBs of log data per month.

### Observability from Day One
- Instrument services before they go to production
- Use **auto-instrumentation** agents for common frameworks
- Define **dashboards** and **alerts** as part of the deployment process
- **Staff insight**: Don't retrofit observability. Add metrics, structured logging, and tracing as part of the initial service scaffold. It's 10x harder to add later when you're in the middle of a production incident.

### Avoiding Alert Fatigue
- Alert on **symptoms** (user-facing impact), not causes (CPU, memory)
- Use **SLO burn rate** for alerting — ties alerts to error budget
- **Staff insight**: If your team gets more than 5-10 meaningful alerts per day, you have alert fatigue. Engineers start ignoring alerts, and real incidents get missed. Consolidate alerts, raise thresholds, and focus on user impact.
