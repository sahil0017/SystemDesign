# Analytics Pipeline Hybrid Database Architecture

## Problem Statement

Design a hybrid database architecture for an analytics pipeline that ingests operational data from OLTP systems, transforms it via streaming, and serves analytical queries on OLAP engines. Use PostgreSQL for transactional data, Kafka for streaming, and ClickHouse/BigQuery for analytical queries. Handle CDC, ETL/ELT pipelines, materialized views, and data freshness SLAs.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **OLTP Source**: PostgreSQL stores operational data (orders, users, products).
- **Change Capture**: CDC captures inserts, updates, deletes from OLTP.
- **Streaming**: Kafka buffers change events for downstream consumers.
- **Transformation**: ETL/ELT pipeline enriches, joins, and aggregates data.
- **OLAP Storage**: ClickHouse/BigQuery serves analytical queries.
- **Materialized Views**: Pre-aggregated dashboards (daily revenue, user cohorts).
- **Data Freshness**: Real-time (< 5 min) and batch (daily) pipelines.

### Non-Functional Requirements
- **Zero OLTP impact**: CDC must not slow down transactional queries.
- **Exactly-once processing**: No duplicate events in analytics.
- **Schema evolution**: Handle OLTP schema changes without breaking pipeline.
- **Backfill support**: Re-process historical data for new metrics.
- **Query performance**: Analytical queries on billions of rows in < 5 seconds.

## Key Design Decisions

- **CDC via Debezium**: Read database WAL for zero-impact change capture.
- **ELT over ETL**: Transform data in the warehouse (ClickHouse), not before load.
- **Kafka as buffer**: Decouples OLTP from OLAP; enables replay and backfill.
- **Materialized views**: Pre-aggregate common dashboard queries.
- **Data freshness tiers**: Real-time (5 min), near-real-time (1 hour), batch (daily).

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌─────────────┐
│  PostgreSQL │────►│ Debezium │────►│  Kafka   │────►│  Kafka      │
│  (OLTP)     │     │ (CDC)    │     │ (Stream) │     │  Streams    │
└─────────────┘     └──────────┘     └──────────┘     └──────┬──────┘
                                                              │
                                              ┌───────────────┤
                                              │               ▼
                                      ┌───────┴──────┐  ┌─────────────┐
                                      │   Schema     │  │  ClickHouse │
                                      │   Registry   │  │  (OLAP)     │
                                      └──────────────┘  └─────────────┘
                                                              │
                                                              ▼
                                                      ┌─────────────┐
                                                      │  Dashboard  │
                                                      │  (Grafana/  │
                                                      │   Superset) │
                                                      └─────────────┘
```

## Schema Design

### PostgreSQL (OLTP Source)

```sql
-- Example: Orders table (same as e-commerce schema)
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id UUID NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL
);
```

### Kafka Topics

```
# CDC change events from PostgreSQL
Topic: db.orders.changes
Partition key: order_id
Schema: Avro (Debezium envelope)
Retention: 7 days
Partitions: 24

Topic: db.order_items.changes
Partition key: order_id
Schema: Avro
Retention: 7 days
Partitions: 24

# Enriched events after transformation
Topic: analytics.order_events
Partition key: user_id
Schema: Avro
Retention: 30 days
Partitions: 48

# Aggregated metrics
Topic: analytics.daily_metrics
Partition key: metric_date
Schema: Avro
Retention: 90 days
Partitions: 12
```

### Debezium CDC Event Format

```json
{
  "before": null,
  "after": {
    "order_id": 12345,
    "user_id": 67890,
    "status": "completed",
    "total": 99.99,
    "currency": "USD",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "source": {
    "db": "postgres",
    "table": "orders",
    "ts_ms": 1705315800000
  },
  "op": "c",  // "c"=create, "u"=update, "d"=delete
  "ts_ms": 1705315800100
}
```

### ClickHouse (OLAP Target)

```sql
-- Fact table: Orders (wide, denormalized)
CREATE TABLE analytics.orders_fact (
    order_id Int64,
    user_id Int64,
    status LowCardinality(String),
    total Decimal(12,2),
    currency FixedString(3),
    user_country LowCardinality(String),
    user_city LowCardinality(String),
    item_count UInt32,
    avg_item_price Decimal(10,2),
    created_at DateTime,
    updated_at DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, order_id);

-- Materialized view: Daily revenue
CREATE TABLE analytics.daily_revenue (
    metric_date Date,
    country LowCardinality(String),
    order_count UInt64,
    revenue Decimal(18,2),
    avg_order_value Decimal(12,2),
    unique_users UInt64
) ENGINE = AggregatingMergeTree()
ORDER BY (metric_date, country);

CREATE MATERIALIZED VIEW analytics.daily_revenue_mv
TO analytics.daily_revenue
AS SELECT
    toDate(created_at) AS metric_date,
    user_country AS country,
    count() AS order_count,
    sum(total) AS revenue,
    avg(total) AS avg_order_value,
    uniq(user_id) AS unique_users
FROM analytics.orders_fact
GROUP BY metric_date, country;

-- Materialized view: User cohorts
CREATE TABLE analytics.user_cohorts (
    cohort_date Date,
    days_since_signup UInt8,
    active_users UInt64,
    orders UInt64,
    revenue Decimal(18,2)
) ENGINE = SummingMergeTree()
ORDER BY (cohort_date, days_since_signup);
```

## Data Pipeline

### Real-Time Pipeline (Kafka Streams)

```java
// Enrich order events with user data
KStream<String, OrderEvent> orders = builder.stream("analytics.order_events");
KTable<String, UserData> users = builder.table("users_lookup");

orders.join(users, 
    (order, user) -> order.withUserCountry(user.country),
    JoinWindows.ofSizeDuration(Duration.ofMinutes(5)),
    StreamJoined.with(OrderKeySerde, OrderValueSerde, UserValueSerde)
).to("analytics.enriched_orders");
```

### Batch Pipeline (Daily Backfill)

```sql
-- Backfill historical data into ClickHouse
INSERT INTO analytics.orders_fact
SELECT
    o.order_id,
    o.user_id,
    o.status,
    o.total,
    o.currency,
    u.country AS user_country,
    u.city AS user_city,
    COUNT(oi.order_item_id) AS item_count,
    AVG(oi.unit_price) AS avg_item_price,
    o.created_at,
    o.updated_at
FROM postgres.orders o
LEFT JOIN postgres.order_items oi ON o.order_id = oi.order_id
LEFT JOIN postgres.users u ON o.user_id = u.user_id
WHERE o.created_at >= '2024-01-01' AND o.created_at < '2024-01-02'
GROUP BY o.order_id, o.user_id, o.status, o.total, o.currency, u.country, u.city, o.created_at, o.updated_at;
```

## Staff-Level Design Considerations

### CDC via Debezium
- **WAL-based capture**: Debezium reads PostgreSQL's Write-Ahead Log (WAL) for zero-impact change capture.
- **Staff insight**: Never use trigger-based CDC on high-throughput OLTP tables — triggers add latency to every write. WAL-based CDC (Debezium, Logical Decoding) has zero impact on OLTP performance because it reads the WAL, not the tables.

### ELT vs ETL
- **ELT**: Load raw data into ClickHouse, then transform with SQL.
- **Staff insight**: ELT is preferred over ETL because ClickHouse's columnar engine processes transformations faster than any ETL tool. Load raw CDC events into a staging table, then use ClickHouse SQL for joins, aggregations, and materialized views. This simplifies the pipeline and enables ad-hoc reprocessing.

### Data Freshness Trade-offs
- **Real-time**: Kafka Streams → ClickHouse (< 5 min lag).
- **Near-real-time**: Micro-batch every 15 min.
- **Batch**: Daily ETL for complex aggregations.
- **Staff insight**: Not all analytics need real-time. Dashboard KPIs can be near-real-time (15 min). Cohort analysis and ML features are batch (daily). Use the cheapest pipeline that meets the freshness SLA. Real-time pipelines are 10x more complex and expensive than batch.

### Schema Evolution Handling
- **Avro + Schema Registry**: Backward-compatible schema changes.
- **Staff insight**: When OLTP schema changes (e.g., add column to orders), Debezium automatically picks up the new schema. Register the new Avro schema with `BACKWARD` compatibility. ClickHouse handles new columns via `ALTER TABLE ADD COLUMN`. Use `NULL` defaults for new columns in historical data.

### Backfilling Historical Data
- **Direct OLTP → OLAP**: For initial load or reprocessing.
- **Staff insight**: When adding a new metric that requires historical data, don't wait for CDC to catch up. Run a one-time batch job that reads directly from OLTP and inserts into OLAP. Use date-range partitioning to backfill incrementally (one day at a time) to avoid locking OLTP tables.
