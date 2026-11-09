# IoT Time-Series Database Schema Design

## Problem Statement

Design a NoSQL schema for an IoT time-series data platform that ingests sensor data from millions of devices. Store readings (temperature, humidity, pressure) with timestamps, device metadata, and support aggregation queries (avg, min, max over time windows). Handle data retention, late-arriving data, and down-sampling for long-term storage.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Device Registry**: Device ID, type, location, firmware version, owner.
- **Sensor Readings**: Timestamp, metric name, value, unit, quality flag.
- **Aggregations**: Pre-computed avg, min, max, count over 1min, 1hour, 1day windows.
- **Alerts**: Threshold-based alerts (e.g., temperature > 100°F).
- **Data Retention**: Raw data for 30 days, hourly aggregates for 1 year, daily for 5+ years.
- **Device Metadata**: Tags, groups, geolocation for filtering.

### Non-Functional Requirements
- **Write throughput**: 1M+ readings/second from millions of devices.
- **Query latency**: Aggregation queries in < 1 second.
- **Data retention**: Automatic TTL-based expiration.
- **Late data handling**: Accept readings up to 1 hour late without gaps.
- **Compression**: Time-series data compression for storage efficiency.

## Key Design Decisions

- **Partition by device_id + date**: Each device's data for a day is a single partition.
- **Clustering by timestamp**: Enables efficient time-range queries within a partition.
- **Materialized views**: Pre-aggregated metrics at 1min, 1hour, 1day granularity.
- **TTL-based retention**: Automatic expiration of raw data after 30 days.
- **Down-sampling pipeline**: Batch job aggregates raw → hourly → daily.

## Schema Design (Cassandra)

### Device Registry

```cql
CREATE KEYSPACE iot WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': 3};
USE iot;

CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    device_type TEXT,
    owner_id TEXT,
    location TEXT,
    latitude DECIMAL,
    longitude DECIMAL,
    firmware_version TEXT,
    status TEXT, -- 'active', 'inactive', 'maintenance'
    tags MAP<TEXT, TEXT>,
    created_at TIMESTAMP,
    last_seen_at TIMESTAMP
);
```

### Raw Sensor Readings

```cql
-- Partition by device_id + date, cluster by timestamp
CREATE TABLE sensor_readings (
    device_id TEXT,
    reading_date TEXT, -- '2024-01-15'
    timestamp TIMESTAMP,
    metric_name TEXT,
    value DECIMAL,
    unit TEXT,
    quality_flag BOOLEAN,
    PRIMARY KEY ((device_id, reading_date), timestamp, metric_name)
) WITH CLUSTERING ORDER BY (timestamp ASC, metric_name ASC)
  AND default_time_to_live = 2592000; -- 30 days in seconds
```

### 1-Minute Aggregations

```cql
CREATE TABLE readings_1min (
    device_id TEXT,
    bucket_date TEXT,
    bucket_time TIME, -- Truncated to minute
    metric_name TEXT,
    avg_value DECIMAL,
    min_value DECIMAL,
    max_value DECIMAL,
    sum_value DECIMAL,
    count BIGINT,
    sample_value DECIMAL, -- Last value for line charts
    PRIMARY KEY ((device_id, bucket_date, metric_name), bucket_time)
) WITH CLUSTERING ORDER BY (bucket_time ASC)
  AND default_time_to_live = 7776000; -- 90 days
```

### 1-Hour Aggregations

```cql
CREATE TABLE readings_1hour (
    device_id TEXT,
    bucket_date TEXT,
    bucket_hour INT, -- 0-23
    metric_name TEXT,
    avg_value DECIMAL,
    min_value DECIMAL,
    max_value DECIMAL,
    sum_value DECIMAL,
    count BIGINT,
    sample_value DECIMAL,
    PRIMARY KEY ((device_id, bucket_date, metric_name), bucket_hour)
) WITH CLUSTERING ORDER BY (bucket_hour ASC)
  AND default_time_to_live = 31536000; -- 1 year
```

### 1-Day Aggregations

```cql
CREATE TABLE readings_1day (
    device_id TEXT,
    bucket_date TEXT,
    metric_name TEXT,
    avg_value DECIMAL,
    min_value DECIMAL,
    max_value DECIMAL,
    sum_value DECIMAL,
    count BIGINT,
    sample_value DECIMAL,
    PRIMARY KEY ((device_id, metric_name), bucket_date)
) WITH CLUSTERING ORDER BY (bucket_date ASC)
  AND default_time_to_live = 157680000; -- 5 years
```

### Device Alerts

```cql
CREATE TABLE device_alerts (
    device_id TEXT,
    alert_id UUID,
    metric_name TEXT,
    threshold_value DECIMAL,
    operator TEXT, -- 'gt', 'lt', 'gte', 'lte'
    triggered_value DECIMAL,
    severity TEXT, -- 'warning', 'critical'
    acknowledged BOOLEAN,
    triggered_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    PRIMARY KEY (device_id, alert_id)
);
```

### Device Group Index (for multi-device queries)

```cql
CREATE TABLE device_groups (
    group_name TEXT,
    device_id TEXT,
    device_type TEXT,
    location TEXT,
    status TEXT,
    PRIMARY KEY (group_name, device_id)
);
```

## Indexes Strategy

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `sensor_readings` | `(device_id, reading_date), timestamp, metric_name` | Time-range query per device |
| `readings_1min` | `(device_id, bucket_date, metric_name), bucket_time` | Minute-level charting |
| `readings_1hour` | `(device_id, bucket_date, metric_name), bucket_hour` | Hourly dashboard |
| `readings_1day` | `(device_id, metric_name), bucket_date` | Long-term trends |
| `device_alerts` | `device_id, alert_id` | Device's active alerts |
| `device_groups` | `group_name, device_id` | Multi-device queries by group |

## Staff-Level Design Considerations

### Partition Key Choice
- **device_id + date**: Each partition holds one device's data for one day.
- **Staff insight**: Never partition by `timestamp` alone — it creates a hot partition where all writes go to one node. `device_id + date` distributes writes across devices and limits partition size to ~144K readings per device per day (1 per second).

### Data Retention via TTL
- **Automatic expiration**: Cassandra's `default_time_to_live` removes expired data during compaction.
- **Staff insight**: TTL is not immediate — data is marked for deletion during the next compaction cycle. For guaranteed deletion within a time window, use a background purge job. Don't rely on TTL for compliance-critical data deletion.

### Down-Sampling Strategy
- **Pipeline**: Raw (30 days) → 1min (90 days) → 1hour (1 year) → 1day (5 years).
- **Staff insight**: Run a batch job (Spark/Flink) every hour that reads raw data and writes to aggregation tables. Use tumbling windows for 1min/1hour and daily windows for 1day. Handle late-arriving data by allowing upserts within a 1-hour grace period.

### Handling Late-Arriving Data
- **Grace period**: Accept readings up to 1 hour late; reject older data.
- **Staff insight**: Late data is common in IoT (network issues, device sleep modes). Use the same write path for late data — Cassandra handles out-of-order timestamps via the clustering key. For aggregation tables, use `INSERT ... IF NOT EXISTS` (LWT) to avoid overwriting computed aggregates.

### Multi-Device Aggregation Queries
- **Problem**: "Show avg temperature for all devices in group X" requires scanning multiple partitions.
- **Staff insight**: Cassandra is not designed for cross-partition aggregation. For dashboard queries across devices, pre-compute group-level aggregates in a separate table or use a OLAP engine (ClickHouse/Druid) that reads from the same Kafka stream.
