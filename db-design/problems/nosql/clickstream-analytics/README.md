# Clickstream Analytics Database Schema Design

## Problem Statement

Design a NoSQL schema for clickstream analytics that ingests user event data (page views, clicks, conversions) at millions of events per second. Support real-time dashboards, historical analysis, user session reconstruction, and PII data handling.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Event Ingestion**: Page views, clicks, button clicks, form submissions, errors, custom events.
- **Event Properties**: User ID, session ID, page URL, referrer, device info, timestamp.
- **Real-time Dashboards**: Active users, page views, conversion rate, bounce rate.
- **Historical Analysis**: Daily/weekly/monthly trends, funnel analysis, cohort analysis.
- **User Session Reconstruction**: Group events into sessions by user and time gap.
- **Funnel Analysis**: Track user journey through conversion steps.

### Non-Functional Requirements
- **Write throughput**: 5M+ events/second during peak traffic.
- **Query latency**: Real-time dashboard updates in < 5 seconds.
- **Data retention**: Raw events for 90 days, aggregates indefinitely.
- **Schema evolution**: Add new event properties without breaking consumers.
- **PII handling**: Anonymize or exclude personally identifiable information.

## Key Design Decisions

- **Event partitioning by user_id + date**: Enables user behavior queries and time-based retention.
- **Event schema with Avro**: Schema registry for evolution and backward compatibility.
- **Real-time aggregation**: Kafka Streams for tumbling window aggregations.
- **Raw event storage**: S3 + Parquet for cost-effective long-term storage.
- **PII redaction**: Strip PII at ingestion; store hashed user_id for analytics.

## Schema Design (Cassandra + Kafka + S3)

### Raw Events (Cassandra - Hot Data)

```cql
CREATE KEYSPACE analytics WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': 3};
USE analytics;

-- Raw events for real-time queries (90-day retention)
CREATE TABLE raw_events (
    user_id TEXT,
    event_date TEXT, -- '2024-01-15'
    timestamp TIMESTAMP,
    event_id UUID,
    event_type TEXT, -- 'page_view', 'click', 'conversion', 'error'
    page_url TEXT,
    referrer TEXT,
    session_id TEXT,
    device_type TEXT, -- 'desktop', 'mobile', 'tablet'
    browser TEXT,
    os TEXT,
    country TEXT,
    city TEXT,
    properties MAP<TEXT, TEXT>, -- Custom event properties
    PRIMARY KEY ((user_id, event_date), timestamp, event_id)
) WITH CLUSTERING ORDER BY (timestamp ASC, event_id ASC)
  AND default_time_to_live = 7776000; -- 90 days
```

### Real-Time Aggregations (1-Minute Windows)

```cql
-- Active users per minute
CREATE TABLE active_users_1min (
    bucket_date TEXT,
    bucket_minute TIME,
    active_users BIGINT,
    page_views BIGINT,
    clicks BIGINT,
    conversions BIGINT,
    errors BIGINT,
    PRIMARY KEY (bucket_date, bucket_minute)
) WITH CLUSTERING ORDER BY (bucket_minute ASC)
  AND default_time_to_live = 86400; -- 1 day

-- Page views per page per minute
CREATE TABLE page_views_1min (
    page_url TEXT,
    bucket_date TEXT,
    bucket_minute TIME,
    view_count BIGINT,
    unique_visitors BIGINT,
    avg_duration_ms BIGINT,
    PRIMARY KEY ((page_url, bucket_date), bucket_minute)
) WITH CLUSTERING ORDER BY (bucket_minute ASC)
  AND default_time_to_live = 86400;

-- Conversion funnel per minute
CREATE TABLE funnel_1min (
    funnel_step TEXT,
    bucket_date TEXT,
    bucket_minute TIME,
    step_count BIGINT,
    drop_off_count BIGINT,
    conversion_rate DECIMAL,
    PRIMARY KEY ((funnel_step, bucket_date), bucket_minute)
) WITH CLUSTERING ORDER BY (bucket_minute ASC)
  AND default_time_to_live = 86400;
```

### Daily Aggregations

```cql
CREATE TABLE daily_metrics (
    metric_date TEXT,
    metric_name TEXT,
    value BIGINT,
    labels MAP<TEXT, TEXT>, -- {"country": "US", "device": "mobile"}
    PRIMARY KEY ((metric_date, metric_name), labels)
) WITH default_time_to_live = 31536000; -- 1 year
```

### User Sessions

```cql
CREATE TABLE user_sessions (
    user_id TEXT,
    session_id TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    event_count BIGINT,
    page_views BIGINT,
    duration_seconds BIGINT,
    entry_page TEXT,
    exit_page TEXT,
    device_type TEXT,
    country TEXT,
    PRIMARY KEY (user_id, session_id)
);
```

### Kafka Topics

```
# Raw event stream
Topic: events.raw
Partition key: user_id
Schema: Avro (registered in Schema Registry)
Retention: 7 days
Partitions: 100

# Aggregated metrics stream
Topic: events.aggregated.1min
Partition key: metric_name
Schema: Avro
Retention: 1 day
Partitions: 10

# Session completion events
Topic: events.sessions
Partition key: user_id
Schema: Avro
Retention: 30 days
Partitions: 50
```

### Avro Event Schema

```json
{
  "type": "record",
  "name": "ClickEvent",
  "namespace": "com.analytics.events",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "user_id", "type": ["null", "string"], "default": null},
    {"name": "session_id", "type": "string"},
    {"name": "timestamp", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "event_type", "type": "string"},
    {"name": "page_url", "type": "string"},
    {"name": "referrer", "type": ["null", "string"], "default": null},
    {"name": "device_type", "type": "string"},
    {"name": "browser", "type": "string"},
    {"name": "os", "type": "string"},
    {"name": "country", "type": ["null", "string"], "default": null},
    {"name": "properties", "type": {"type": "map", "values": "string"}}
  ]
}
```

### S3 Data Lake (Cold Storage)

```
s3://analytics-data-lake/
├── raw_events/
│   ├── year=2024/month=01/day=15/
│   │   ├── part-00000.parquet
│   │   ├── part-00001.parquet
│   │   └── ...
│   └── ...
├── aggregated/
│   ├── daily/year=2024/month=01/
│   │   ├── daily_metrics_2024-01.parquet
│   │   └── ...
│   └── ...
└── sessions/
    ├── year=2024/month=01/
    │   ├── sessions_2024-01.parquet
    │   └── ...
```

## Indexes Strategy

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `raw_events` | `(user_id, event_date), (timestamp, event_id)` | User's events by day |
| `active_users_1min` | `bucket_date, bucket_minute` | Real-time active user chart |
| `page_views_1min` | `(page_url, bucket_date), bucket_minute` | Page-level real-time metrics |
| `funnel_1min` | `(funnel_step, bucket_date), bucket_minute` | Conversion funnel |
| `daily_metrics` | `(metric_date, metric_name), labels` | Daily dashboard metrics |
| `user_sessions` | `user_id, session_id` | User's session history |

## Staff-Level Design Considerations

### Event Schema Evolution
- **Avro + Schema Registry**: Backward-compatible schema changes (add optional fields).
- **Staff insight**: Never break existing consumers. Use Avro's default values for new fields. When removing a field, mark it as deprecated for one release cycle. Use Confluent Schema Registry with `BACKWARD` compatibility mode to enforce this.

### Real-Time Aggregation
- **Kafka Streams**: Tumbling windows (1 min) for real-time dashboards.
- **Staff insight**: Use Kafka Streams' `windowKTable` for counting events per minute. The KTable handles late-arriving events within the window grace period. For sessionization, use `sessionWindows()` with a 30-minute inactivity gap to group events into sessions.

### Raw Event Storage
- **S3 + Parquet**: Columnar format for cost-effective analytical queries.
- **Staff insight**: Don't store raw events in Cassandra indefinitely — it's expensive. Use Cassandra for the hot 90-day window and stream to S3 in Parquet format for long-term storage. Query cold data with Athena/Spark SQL. Parquet's columnar format is 10x smaller than JSON and enables column-pruning for fast queries.

### PII Data Handling
- **Redaction at ingestion**: Strip email, name, phone from events before storage.
- **Staff insight**: Hash user_id with a salt for analytics: `SHA256(user_id + salt)`. This allows user tracking without exposing PII. Never store raw PII in analytics tables. For GDPR deletion, maintain a mapping table (user_id → hashed_id) in a secure vault so you can locate and delete hashed records on request.

### User Session Reconstruction
- **30-minute gap**: Events within 30 minutes of each other belong to the same session.
- **Staff insight**: Don't compute sessions at query time — it's expensive. Use Kafka Streams session windows to assign session IDs at ingestion. Store the sessionized data in a separate table for fast session-based queries. Session windows are merged when events from the same user arrive within the gap duration.
