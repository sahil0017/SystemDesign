# Distributed Tracing

## Overview

Distributed tracing tracks requests as they flow through microservices, providing visibility into latency, dependencies, and errors. Tools like Jaeger, Zipkin, and OpenTelemetry make distributed tracing accessible for production systems.

## Core Concepts

### Trace and Span
- **Trace**: Complete journey of a request through the system (unique trace ID)
- **Span**: Single operation within a trace (e.g., database call, HTTP request)
- **Root span**: First span in a trace (entry point)
- **Child span**: Span created by another span

```
Trace: abc123
  Span 1: API Gateway receives request (0-100ms)
    Span 2: User Service lookup (5-30ms)
      Span 3: Database query (8-25ms)
    Span 4: Order Service create (35-90ms)
      Span 5: Payment Service charge (40-85ms)
```

### Context Propagation
- **W3C Trace Context**: Standard headers (`traceparent`, `tracestate`)
- Each service extracts trace context from incoming request and propagates it
- Missing context propagation breaks the trace chain

### Sampling
- **Head-based**: Decide at trace start — low overhead, may miss important traces
- **Tail-based**: Decide after collection — retains errors/slow traces, higher cost
- **Probabilistic**: Fixed sampling rate (e.g., 1%) — simple but unpredictable

## Architecture

```
Service A          Service B          Collector          Storage          Query UI
    |                  |                  |                  |               |
    |--[span]--------->|--[span]--------->|----------------->|--query------->|
    |<--[span end]-----|<--[span end]-----|                  |               |
```

## Implementation with OpenTelemetry

### Auto-Instrumentation
- Java: Agent JAR automatically instruments HTTP clients, databases, frameworks
- No code changes needed for common libraries
- Custom spans for business logic

### Manual Instrumentation
```java
Span span = tracer.spanBuilder("processOrder").startSpan();
try (Scope scope = span.makeCurrent()) {
    // business logic
    span.setAttribute("order.id", orderId);
} finally {
    span.end();
}
```

## Staff-Level Insights

### Sampling Strategy
- Use **hybrid sampling**: 1% head-based + 100% tail-based for errors and slow traces
- This ensures you always capture failures while keeping costs manageable
- **Staff insight**: Don't trace everything at 100%. A high-traffic service generating 10K RPS would produce terabytes of trace data daily. Sampling is essential for cost control.

### Context Propagation Pitfalls
- Ensure **all** integration points propagate context: HTTP, gRPC, Kafka, databases, cron jobs
- Use middleware/interceptors to automate propagation
- **Staff insight**: The most common tracing bug is **missing context propagation** at one integration point. Use a checklist: every outgoing call (HTTP, message, DB) must carry trace context.

### Storage and Cost Management
- **Hot storage** (Elasticsearch): Last 7 days for fast querying
- **Warm storage** (S3 + Parquet): 30-90 days for analysis
- **Cold storage**: Archived traces for compliance
- **Staff insight**: Trace data grows fast. Implement **tiered storage** from day one. Elasticsearch for recent traces, S3 for long-term. A single service can generate TBs of trace data per month at high scale.
