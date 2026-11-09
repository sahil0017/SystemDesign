# Ad Click Event Aggregation

## Problem Statement

Design an ad click event aggregation system like Google Ads that processes billions of ad impression and click events in real-time, providing near-real-time analytics and reporting.

**Reference**: ByteByteGo

## Requirements

### Functional Requirements
- **Event ingestion**: Accept ad impression and click events at high throughput.
- **Aggregation**: Count impressions, clicks, and CTR by ad, campaign, advertiser, and time window.
- **Real-time dashboard**: Near-real-time metrics with 1-5 minute delay.
- **Historical reporting**: Daily, weekly, monthly reports with historical data.
- **Fraud detection**: Detect suspicious click patterns (click farms, bots).

### Non-Functional Requirements
- **Throughput**: 100M+ events per day; 10K+ events per second peak.
- **Latency**: Dashboard updates within 5 minutes of event.
- **Accuracy**: Event counts accurate to within 1%.

## Key Design Decisions
- **Stream processing**: Kafka + Flink/Spark Streaming for real-time aggregation.
- **Lambda architecture**: Speed layer (real-time) + batch layer (accurate) + serving layer.
- **Approximate counting**: HyperLogLog for unique visitor counting with small memory footprint.
- **Time windows**: Tumbling windows (1 minute) for real-time; daily windows for batch.

## Architecture Overview

```
Ad Servers → Kafka (ad_events topic)
                    ↓
            ┌──────────────┐
            │  Flink Job   │→ Real-time Aggregates → Redis → Dashboard
            │ (streaming)  │
            └──────────────┘
                    ↓
            ┌──────────────┐
            │  Spark Job   │→ Daily Aggregates → Data Warehouse → Reports
            │ (batch)      │
            └──────────────┘
```

## Staff-Level Design Considerations

### Lambda Architecture
- **Speed layer**: Flink processes events in real-time with 1-minute tumbling windows. Results go to Redis for dashboard.
- **Batch layer**: Spark processes raw events from Kafka/HDFS daily. Results go to a data warehouse (BigQuery/Redshift).
- **Staff insight**: The speed layer is fast but approximate (events may be duplicated or lost). The batch layer is slow but accurate. Merge results at serving time, preferring batch when available.

### Approximate Counting
- **HyperLogLog**: Count unique visitors with < 2% error using only 1.5KB of memory per counter.
- **Staff insight**: A HashMap for unique counting requires O(n) memory. HyperLogLog uses O(log log n) memory. For 100M unique visitors, HLL uses ~1.5KB vs ~2GB for a hash set.

### Event Deduplication
- **Idempotency key**: Each event has a unique ID. Use a Bloom filter to detect duplicates in the streaming layer.
- **Staff insight**: Ad servers retry on network failures, causing duplicate events. Deduplicate at ingestion time using a sliding window Bloom filter (last 5 minutes). This catches 99% of duplicates.
