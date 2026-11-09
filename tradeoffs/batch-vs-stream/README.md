# Batch vs Stream Processing

## Trade-off Overview

Batch processing processes large volumes of data in groups at scheduled intervals. Stream processing processes data item-by-item in real-time as it arrives.

## Batch Processing (Hadoop, Spark)
- **Pros**: High throughput, cost-effective, fault-tolerant, simplified complexity.
- **Cons**: High latency (hours/days), not real-time, resource-intensive jobs.
- **Use when**: Daily reports, ETL, ML training, historical analysis.

## Stream Processing (Kafka Streams, Flink, Spark Streaming)
- **Pros**: Low latency (milliseconds), real-time insights, event-driven.
- **Cons**: Complex to implement, harder to debug, higher cost per record.
- **Use when**: Real-time alerts, fraud detection, live dashboards, monitoring.

## Staff-Level Insight

> "Lambda architecture uses both: batch for correctness, speed (stream) for latency."

- **Staff insight**: Use **streaming for real-time alerts** (fraud detection, anomaly detection) and **batch for historical analysis** (daily reports, ML training). Don't try to do everything with streaming — batch is cheaper and more reliable for large-scale historical processing. Use **Kafka as the backbone** — stream processors read from Kafka in real-time; batch jobs read from Kafka's persistent logs.
