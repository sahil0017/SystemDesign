# IoT Ingestion Pipeline

## Problem Statement

Design an IoT data ingestion pipeline that collects, processes, and stores telemetry data from millions of connected devices (sensors, vehicles, smart home devices). The system must handle high-throughput data ingestion, real-time processing, and long-term storage with cost optimization.

**Reference**: Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Device registration**: Register devices with metadata, capabilities, and authentication.
- **Data ingestion**: Accept telemetry data via MQTT, HTTP, or WebSocket.
- **Real-time processing**: Filter, aggregate, and transform data in real-time.
- **Alerting**: Trigger alerts when sensor values exceed thresholds.
- **Data storage**: Store raw data for analysis and aggregated data for dashboards.
- **Device commands**: Send commands to devices (firmware updates, configuration changes).
- **Data retention**: Configurable retention policies (hot/warm/cold storage).

### Non-Functional Requirements
- **Scale**: 10M+ devices; 1B+ messages per day; 100K+ messages per second.
- **Latency**: Ingestion to processing < 1 second; alerting < 5 seconds.
- **Reliability**: No data loss on network interruption; buffer and retry.
- **Cost**: Optimize storage costs with tiered storage (hot/warm/cold).

## Key Design Decisions
- **MQTT protocol**: Lightweight publish-subscribe protocol for IoT devices.
- **Kafka**: High-throughput message queue for ingestion and processing.
- **Time-series database**: Optimized storage for time-stamped sensor data.
- **Stream processing**: Real-time aggregation and alerting with Flink/Spark Streaming.

## Architecture Diagram

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Devices  │───►│  MQTT Broker │───►│   Kafka      │───►│  Stream      │
│ (Sensors)│    │  (Ingestion) │    │  (Buffer)    │    │  Processor   │
└──────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                               │
                                                    ┌──────────┼──────────┐
                                                    │          │          │
                                           ┌────────┴┐  ┌─────┴──┐ ┌────┴─────┐
                                           │ Time-  │  │ Alert  │ │ Dashboard │
                                           │ Series │  │ Engine │ │ (Aggreg)  │
                                           │ DB     │  │        │ │           │
                                           └────────┘  └────────┘ └───────────┘
```

## Staff-Level Design Considerations

### MQTT vs HTTP
- **MQTT**: Lightweight, publish-subscribe, QoS levels, retained messages. Ideal for constrained devices.
- **HTTP**: Universal, stateless, but heavier overhead. Good for devices with good connectivity.
- **Staff insight**: Use MQTT for battery-constrained devices (low overhead, QoS 1 for at-least-once delivery). Use HTTP/HTTPS for devices with good connectivity. Support both protocols with an adapter layer.

### Kafka for Ingestion
- **Partitioning**: Partition by device ID for per-device ordering.
- **Staff insight**: Use Kafka as the backbone — it handles backpressure, replay, and multiple consumers. Partition by device ID so all messages from one device are ordered. Use compacted topics for device state (last known value).

### Time-Series Storage
- **Specialized DB**: InfluxDB, TimescaleDB, or Prometheus optimized for time-series data.
- **Staff insight**: Don't use PostgreSQL for time-series data — it's not optimized for high-write, time-range queries. Use a time-series database with built-in downsampling, retention policies, and compression.

### Tiered Storage
- **Hot**: Recent data in memory/SSD for real-time queries (last 7 days).
- **Warm**: Compressed data on disk for historical queries (last 90 days).
- **Cold**: Archived data in S3/Glacier for compliance (1+ years).
- **Staff insight**: 80% of queries access the last 7 days of data. Use tiered storage to optimize costs — hot data is expensive but fast, cold data is cheap but slow. Automate data migration between tiers.
