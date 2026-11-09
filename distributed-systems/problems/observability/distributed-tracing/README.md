# Distributed Tracing

## Problem Statement

Design a distributed tracing system (like Jaeger, Zipkin, or OpenTelemetry) that tracks requests as they flow through microservices. The system should capture latency, dependencies, errors, and provide visualization for debugging production issues in distributed systems.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Trace context propagation**: Pass trace ID and span ID across service boundaries via HTTP headers or message metadata.
- **Span collection**: Each service creates spans with start/end time, operation name, tags, and logs.
- **Sampling**: Configurable sampling rate to reduce overhead (head-based, tail-based, probabilistic).
- **Storage**: Store traces for querying and analysis with configurable retention.
- **Querying**: Search traces by trace ID, service name, operation, duration, error status, custom tags.
- **Visualization**: Service dependency graph, trace waterfall, flame graphs.
- **Alerting**: Alert on latency SLA breaches, error rate spikes, or dependency failures.

### Non-Functional Requirements
- **Low overhead**: Tracing should add < 1% latency to production requests.
- **High throughput**: Handle 1M+ spans per second during peak traffic.
- **Reliability**: Tracing system failure must not affect production services.
- **Scalability**: Horizontally scale collectors and storage independently.

## Key Design Decisions
- **OpenTelemetry standard**: Use industry-standard format for interoperability.
- **Async collection**: Agents send spans asynchronously to avoid blocking application threads.
- **Tail-based sampling**: Make sampling decisions after collecting all spans — retain important traces regardless of initial sample rate.
- **Tiered storage**: Hot traces in memory/Elasticsearch, warm traces in S3, cold traces archived.

## Architecture

```
Service A          Service B          Service C
   |                  |                  |
   |--[span A1]------>|                  |
   |                  |--[span B1]------>|
   |                  |                  |--[span C1]
   |                  |                  |
   |<--[span A1 end]--|<--[span B1 end]--|<--[span C1 end]
   |                  |                  |
   v                  v                  v
   +-------- Collector --------+
   |  Agent --> gRPC --> Queue --> Storage
   +---------------------------+
              |
              v
        Query & UI Layer
```

## Staff-Level Design Considerations

### Sampling Strategies
- **Head-based**: Decide at trace start — low overhead but may drop critical traces (errors, slow requests).
- **Tail-based**: Decide after all spans collected — retains important traces but higher storage cost.
- **Probabilistic**: Random sampling at fixed rate — simple but unpredictable.
- **Staff insight**: Use **hybrid sampling** — head-based at 1% for cost control, plus tail-based for all error/slow traces. This ensures you always capture failures while keeping costs manageable.

### Context Propagation
- **W3C Trace Context**: Standard headers (`traceparent`, `tracestate`) for cross-service propagation.
- **Message queues**: Pass trace context in message metadata (Kafka headers, RabbitMQ headers).
- **Staff insight**: Ensure **all** integration points propagate context — HTTP, gRPC, Kafka, databases, cron jobs. Missing one link breaks the entire trace. Use middleware/interceptors to automate propagation.

### Storage Design
- **Elasticsearch**: Full-text search on spans, good for recent traces (< 7 days).
- **S3 + Parquet**: Cost-effective long-term storage; query with Athena/Spark.
- **Staff insight**: Use **tiered storage** — Elasticsearch for last 7 days, S3 Parquet for 90+ days. A single high-traffic service can generate terabytes of trace data daily; Elasticsearch alone is prohibitively expensive.

### Overhead Management
- **Batch sending**: Collect spans in memory, flush every 5 seconds or 100 spans.
- **Async agent**: Separate process (sidecar) collects spans — zero impact on application.
- **Staff insight**: Use **OpenTelemetry SDK with batch exporter** — spans are collected in a ring buffer and sent asynchronously. If the collector is down, spans are dropped gracefully without blocking the application.

### Service Dependency Graph
- **Span relationships**: Parent-child relationships between spans reveal service dependencies.
- **Staff insight**: Aggregate span data to build a **real-time dependency graph**. This reveals hidden dependencies (e.g., Service A calls Service C through Service B) and helps impact analysis during incidents.
