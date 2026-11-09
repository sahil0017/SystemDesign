# Metrics Monitoring and Alerting System

## Problem Statement

Design a metrics monitoring and alerting system like Prometheus + Grafana that collects metrics from distributed services, stores time-series data, provides dashboards, and triggers alerts on threshold violations.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Metric collection**: Pull-based (scraping) and push-based metric collection.
- **Time-series storage**: Store metrics with timestamps; configurable retention.
- **Querying**: Flexible queries with aggregation (avg, sum, count, percentile).
- **Dashboards**: Real-time visualizations; customizable panels.
- **Alerting**: Define alert rules; notify via email, Slack, PagerDuty.
- **Labels/Tags**: Dimensional metrics with labels for filtering and grouping.

### Non-Functional Requirements
- **Scale**: 1M+ time series; 100K+ metrics per second; 10K+ services.
- **Latency**: Query response < 1s; alert evaluation < 30s.
- **Retention**: Store high-resolution data for 7 days; downsampled for 1 year.

## Key Design Decisions
- **Pull-based scraping**: Metrics server scrapes targets on a schedule (default: 15s).
- **TSDB**: Time-series database (Prometheus) with chunked storage and compression.
- **Downsampling**: Aggregate old data (1min → 5min → 1hr) to save storage.
- **Alertmanager**: Separate service for alert evaluation, deduplication, and routing.

## Architecture Overview

```
Services → (expose /metrics endpoint)
                    ↑ scraped by
             ┌──────────────┐
             │  Scraper     │→ Time-Series DB (Prometheus)
             └──────────────┘     ↓
                          ┌──────────────┐
                          │  Query Engine│→ Grafana Dashboards
                          └──────────────┘
                          ┌──────────────┐
                          │ Alertmanager │→ Slack, Email, PagerDuty
                          └──────────────┘
```

## Staff-Level Design Considerations

### Time-Series Storage
- **Chunked storage**: Group metrics into 2-hour chunks. Each chunk is compressed (Gorilla encoding for floats).
- **Staff insight**: Gorilla encoding achieves 10-50x compression for time-series data by storing deltas between consecutive values. This is why Prometheus can store 1M series on a single server.

### Downsampling Strategy
- **Continuous merge**: Keep raw data for 7 days, 1-minute aggregates for 30 days, 1-hour aggregates for 1 year.
- **Staff insight**: Don't delete raw data — downsample it. A 1-minute avg of CPU usage is sufficient for 30-day trends. This reduces storage by 99% while preserving useful insights.

### Alert Evaluation
- **Rule engine**: Evaluate alert rules on a schedule (e.g., every 30s). Use PromQL for flexible expressions.
- **Staff insight**: Use inhibition rules to prevent alert storms. If "server down" fires, suppress "high latency" alerts for that server. This reduces noise by 80% in production.
