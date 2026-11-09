# Distributed Metrics Monitoring

## Problem Statement

Design a distributed metrics monitoring system (like Prometheus, Datadog, or Grafana Cloud) that collects, stores, and visualizes time-series metrics from microservices, infrastructure, and applications. The system must support high-cardinality metrics, real-time alerting, aggregation queries, and long-term retention at scale.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Metric collection**: Pull-based (scraping) and push-based (agent/SDK) metric collection.
- **Metric types**: Counters, gauges, histograms, summaries.
- **Labels/Tags**: Key-value dimensions for filtering and grouping (service, host, endpoint).
- **Storage**: Time-series database with compression and retention policies.
- **Querying**: PromQL-like query language for aggregation, filtering, and transformation.
- **Alerting**: Define alert rules based on metric thresholds; notify via Slack, PagerDuty, email.
- **Dashboards**: Visualize metrics with graphs, tables, and heatmaps.

### Non-Functional Requirements
- **High throughput**: Ingest 10M+ metric samples per second.
- **Low latency**: Query response in < 1 second for recent data.
- **Retention**: Store raw metrics for 30 days, downsampled for 1 year.
- **Scalability**: Handle 1M+ unique time-series across services.

## Key Design Decisions
- **Pull-based scraping**: Metrics server scrapes targets on fixed intervals (15-60s).
- **Time-series DB**: Store metrics in columnar format with compression (e.g., TSDB, VictoriaMetrics).
- **Downsampling**: Aggregate raw metrics into 5min/1hour buckets for long-term retention.
- **Federation**: Multiple metrics clusters federate to a global query layer.

## Architecture

```
Services/Hosts              Metrics Server              Storage
      |                          |                        |
      |-- /metrics endpoint ---->| (Scrape every 15s)   |
      |-- Agent push ----------->|                        |
      |                          |-- Write ------------->| TSDB (Raw, 30 days)
      |                          |                        |
      |                          |-- Downsample -------->| TSDB (5min, 1 year)
      |                          |                        |
      |<-- Query (PromQL) ------|<-- Read --------------|
      |                          |
      +-- Alert Manager --> Slack/PagerDuty/Email
```

## Staff-Level Design Considerations

### Pull vs Push Collection
- **Pull (scraping)**: Metrics server pulls from targets — handles target failure gracefully, no agent needed.
- **Push (agent)**: Targets push metrics to server — better for batch jobs and ephemeral containers.
- **Staff insight**: Use **pull-based for long-running services** (scrape `/metrics` endpoint). Use **pushgateway for batch jobs** that don't live long enough to be scraped. For Kubernetes, use **service monitors** that auto-discover pods — no manual target configuration.

### Cardinality Management
- **High cardinality**: Labels with unbounded values (user_id, request_id) create millions of time-series.
- **Cardinality explosion**: A single metric with 1M unique user_ids × 100 endpoints = 100M time-series.
- **Staff insight**: **Never use high-cardinality labels** in metrics. Use `user_id` in logs/traces, not metrics. If you need per-user aggregation, use a separate analytics system (ClickHouse, BigQuery). Metrics are for system-level aggregation, not per-entity tracking. Set cardinality limits and alert when exceeded.

### Storage and Compression
- **Columnar format**: Store metrics by value, not by row — compresses well for time-series data.
- **Gorilla compression**: Delta-of-delta encoding for timestamps; achieves 10-20x compression.
- **Staff insight**: Use **dedicated TSDB** (VictoriaMetrics, Thanos, Cortex) instead of Elasticsearch for metrics. TSDBs use columnar compression optimized for time-series — 10x smaller storage than Elasticsearch. Elasticsearch is better for logs where full-text search is needed.

### Downsampling Strategy
- **Raw data**: Store individual samples for 30 days (high resolution).
- **5-minute aggregates**: Store avg/min/max/sum for 1 year.
- **1-hour aggregates**: Store avg/min/max/sum for 5+ years.
- **Staff insight**: Use **pre-aggregated buckets** for long-term retention. Instead of storing every sample, store 5-minute aggregates (avg, min, max, sum, count). This reduces storage by 120x while preserving ability to answer most queries. Raw data is only needed for recent incident investigation.

### Alerting Best Practices
- **Alert on symptoms, not causes**: Alert on "high error rate" not "CPU is high."
- **Hysteresis**: Different thresholds for alert and resolve to prevent flapping.
- **Staff insight**: Use **recording rules** for complex alert expressions. Pre-compute expensive queries (e.g., `histogram_quantile(0.99, rate(http_duration_seconds_bucket[5m]))`) and store as a metric. This avoids computing the same expression for every alert evaluation. Set alert resolution threshold lower than firing threshold (e.g., fire at >5% error rate, resolve at <3%) to prevent flapping.
