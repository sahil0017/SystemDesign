# Streaming Analytics

## Problem Statement

Design a real-time streaming analytics system that processes continuous data streams (clicks, transactions, logs) to generate real-time dashboards, detect anomalies, and trigger alerts. The system must handle high-throughput data with low-latency processing and accurate aggregations.

**Reference**: Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Data ingestion**: Accept streaming data from multiple sources (Kafka, Kinesis, WebSocket).
- **Windowing**: Time-based windows (tumbling, sliding, session) for aggregations.
- **Aggregations**: Count, sum, average, percentile, and custom metrics in real-time.
- **Dashboard**: Real-time visualizations with auto-refresh.
- **Alerting**: Trigger alerts when metrics exceed thresholds or anomalies are detected.
- **Historical queries**: Query past aggregations for comparison and trend analysis.
- **Join operations**: Join streaming data with reference data (user profiles, product catalog).

### Non-Functional Requirements
- **Scale**: 1M+ events per second; 100+ concurrent dashboards.
- **Latency**: Event to dashboard update < 2 seconds.
- **Accuracy**: Exactly-once processing for financial metrics; at-least-once for analytics.
- **Fault tolerance**: No data loss on processor failure; automatic recovery.

## Key Design Decisions
- **Stream processing engine**: Apache Flink for exactly-once semantics and low latency.
- **Windowing**: Tumbling windows for fixed intervals; sliding windows for overlapping aggregations.
- **State management**: Checkpointed state for fault tolerance and recovery.
- **Materialized views**: Pre-computed aggregations stored in a fast query engine (ClickHouse/Druid).

## Architecture Diagram

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Sources │───►│   Kafka      │───►│  Flink       │───►│  ClickHouse  │
│ (Events) │    │  (Ingestion) │    │  (Processing)│    │  (Query)     │
└──────────┘    └──────────────┘    └──────┬───────┘    └──────┬───────┘
                                           │                   │
                                    ┌──────┴───────┐    ┌──────┴───────┐
                                    │  State       │    │  Dashboard   │
                                    │  Backend     │    │  Service     │
                                    │ (RocksDB)    │    └──────┬───────┘
                                    └──────────────┘           │
                                                     ┌────────┴────────┐
                                                     │    Alert       │
                                                     │    Engine      │
                                                     └────────────────┘
```

## Staff-Level Design Considerations

### Flink vs Spark Streaming
- **Flink**: True stream processing; exactly-once; low latency (sub-second). Native windowing and state management.
- **Spark Streaming**: Micro-batch processing; ~1 second latency; at-least-once by default.
- **Staff insight**: Use Flink for true real-time processing (sub-second latency, exactly-once). Use Spark Streaming for batch-like processing where ~1 second latency is acceptable. Flink is the industry standard for streaming analytics.

### Windowing Strategies
- **Tumbling**: Fixed, non-overlapping windows (e.g., 1-minute buckets). Simple but rigid.
- **Sliding**: Overlapping windows (e.g., 10-minute window every 1 minute). More flexible but higher computation.
- **Session**: Dynamic windows based on activity gaps. Good for user behavior analysis.
- **Staff insight**: Choose windowing based on the business question. "How many events per minute?" → tumbling. "What's the 10-minute moving average?" → sliding. "How long does a user session last?" → session.

### Exactly-Once Processing
- **Checkpointing**: Flink periodically checkpoints state to durable storage (HDFS/S3).
- **Two-phase commit**: Sink supports two-phase commit for exactly-once writes.
- **Staff insight**: Exactly-once is expensive. Use it only for financial metrics where duplicates are unacceptable. For analytics dashboards, at-least-once with idempotent sinks is sufficient and cheaper.

### Materialized Views
- **Pre-computation**: Compute aggregations in Flink and store in ClickHouse/Druid for fast queries.
- **Staff insight**: Don't compute aggregations on every dashboard request — it's too slow. Pre-compute and store in a columnar database optimized for analytical queries. ClickHouse handles billions of rows with sub-second query latency.
