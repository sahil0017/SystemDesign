# Change Data Capture (CDC) Pipeline

## Problem Statement

Design a Change Data Capture (CDC) pipeline that captures database changes in real-time and streams them to downstream systems: cache invalidation, search index updates, data warehouse sync, and event sourcing. Handle WAL-based capture, exactly-once processing, schema registry, and event ordering.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Change Capture**: Detect inserts, updates, and deletes from source database.
- **Event Streaming**: Publish changes to Kafka topics by table.
- **Cache Invalidation**: Remove stale entries from Redis on data changes.
- **Search Index Sync**: Update Elasticsearch index on document changes.
- **Data Warehouse Sync**: Stream changes to ClickHouse/BigQuery for analytics.
- **Event Sourcing**: Use CDC events as the source of truth for domain events.

### Non-Functional Requirements
- **Zero OLTP impact**: CDC must not add latency to transactional queries.
- **Exactly-once processing**: Each change is processed exactly once downstream.
- **Event ordering**: Changes for the same record are processed in order.
- **Schema evolution**: Handle DDL changes (add/drop columns) gracefully.
- **Monitoring**: Track CDC lag, error rates, and throughput.

## Key Design Decisions

- **WAL-based CDC**: Debezium reads database Write-Ahead Log for zero-impact capture.
- **Kafka as event bus**: Decouples CDC from consumers; enables replay and scaling.
- **Idempotent consumers**: Downstream systems handle duplicate events safely.
- **Schema Registry**: Avro schemas ensure contract compatibility.
- **Per-table topics**: Each table has its own Kafka topic for independent consumption.

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌──────────┐
│  PostgreSQL │────►│ Debezium │────►│  Kafka   │
│  (Source)   │     │ (CDC)    │     │ (Topics) │
└─────────────┘     └──────────┘     └────┬─────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              ┌─────┴──────┐      ┌───────┴──────┐      ┌───────┴──────┐
              │ Cache       │      │ Search       │      │ Data         │
              │ Invalidation│      │ Indexer      │      │ Warehouse    │
              │ (Redis)     │      │ (Elasticsearch)│    │ (ClickHouse) │
              └─────────────┘      └──────────────┘      └──────────────┘
```

## Schema Design

### Kafka Topics

```
# CDC change events per table
Topic: db.public.users
Partition key: user_id (from PK)
Schema: Avro (Debezium envelope)
Retention: 7 days
Partitions: 24
Replication: 3

Topic: db.public.orders
Partition key: order_id
Schema: Avro
Retention: 7 days
Partitions: 24

Topic: db.public.products
Partition key: product_id
Schema: Avro
Retention: 7 days
Partitions: 12
```

### Debezium CDC Event Format

```json
{
  "schema": {
    "type": "struct",
    "name": "db.public.users.Value",
    "fields": [
      {
        "name": "before",
        "type": {
          "type": "struct",
          "fields": [
            {"name": "user_id", "type": "long"},
            {"name": "email", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "status", "type": "string"},
            {"name": "updated_at", "type": {"type": "int64", "logicalType": "timestamp-millis"}}
          ]
        },
        "optional": true
      },
      {
        "name": "after",
        "type": {"$ref": "#/schema/fields/0/schema"},
        "optional": true
      },
      {
        "name": "source",
        "type": {
          "type": "struct",
          "fields": [
            {"name": "version", "type": "string"},
            {"name": "connector", "type": "string"},
            {"name": "db", "type": "string"},
            {"name": "schema", "type": "string"},
            {"name": "table", "type": "string"},
            {"name": "ts_ms", "type": "int64"},
            {"name": "lsn", "type": "string"},
            {"name": "txId", "type": "int64"}
          ]
        }
      },
      {"name": "op", "type": "string"},
      {"name": "ts_ms", "type": "int64"}
    ]
  },
  "payload": {
    "before": {
      "user_id": 12345,
      "email": "old@example.com",
      "name": "John Doe",
      "status": "active",
      "updated_at": 1705315800000
    },
    "after": {
      "user_id": 12345,
      "email": "new@example.com",
      "name": "John Doe",
      "status": "active",
      "updated_at": 1705315801000
    },
    "source": {
      "version": "2.4.0",
      "connector": "postgresql",
      "db": "app_db",
      "schema": "public",
      "table": "users",
      "ts_ms": 1705315801000,
      "lsn": "1/2345678",
      "txId": 98765
    },
    "op": "u",
    "ts_ms": 1705315801100
  }
}
```

### CDC Monitoring Table

```sql
CREATE TABLE cdc_monitoring (
    check_id BIGINT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    kafka_topic VARCHAR(255) NOT NULL,
    last_lsn VARCHAR(50),
    current_lsn VARCHAR(50),
    lag_bytes BIGINT,
    lag_seconds DECIMAL(10,2),
    events_per_second DECIMAL(12,2),
    error_count BIGINT DEFAULT 0,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cdc_monitoring_time ON cdc_monitoring(checked_at DESC);
```

### Dead Letter Queue Schema

```json
{
  "TableName": "CDCDeadLetterQueue",
  "KeySchema": [
    { "AttributeName": "event_id", "KeyType": "HASH" },
    { "AttributeName": "timestamp", "KeyType": "RANGE" }
  ]
}

# DLQ entry
{
  "event_id": "uuid-123",
  "timestamp": "2024-01-15T10:30:00Z",
  "topic": "db.public.users",
  "partition": 5,
  "offset": 12345,
  "consumer_group": "cache-invalidation",
  "error_type": "SerializationError",
  "error_message": "Unknown field: new_column",
  "raw_event": "{...}",
  "retry_count": 3
}
```

## Consumer Implementations

### Cache Invalidation Consumer

```python
class CacheInvalidationConsumer:
    def __init__(self, kafka_consumer, redis_client):
        self.kafka = kafka_consumer
        self.redis = redis_client
    
    def process_event(self, event):
        op = event.payload.op
        table = event.payload.source.table
        pk = event.payload.after.user_id if event.payload.after else event.payload.before.user_id
        
        if op in ('u', 'd'):
            # Delete cache keys for this entity
            keys_to_delete = [
                f"user:{pk}",
                f"user:profile:{pk}",
                f"user:preferences:{pk}"
            ]
            self.redis.delete(*keys_to_delete)
            
            # Also invalidate list indexes
            self.redis.zrem("users:active", pk)
        
        # Acknowledge exactly-once via idempotent processing
        # Cache deletion is idempotent: deleting non-existent key is a no-op
```

### Search Index Sync Consumer

```python
class SearchIndexConsumer:
    def __init__(self, kafka_consumer, es_client):
        self.kafka = kafka_consumer
        self.es = es_client
        self.offset_store = OffsetStore()  # Stores committed offsets
    
    def process_event(self, event):
        op = event.payload.op
        table = event.payload.source.table
        doc_id = self.extract_pk(event, table)
        
        try:
            if op == 'c':
                doc = self.transform_to_es_doc(event.payload.after, table)
                self.es.index(index=f"{table}_idx", id=doc_id, body=doc)
            elif op == 'u':
                doc = self.transform_to_es_doc(event.payload.after, table)
                self.es.index(index=f"{table}_idx", id=doc_id, body=doc)
            elif op == 'd':
                self.es.delete(index=f"{table}_idx", id=doc_id, ignore=(404,))
            
            # Commit offset only after successful ES operation
            self.offset_store.commit(event.topic, event.partition, event.offset)
        except Exception as e:
            # Send to DLQ for manual retry
            self.send_to_dlq(event, str(e))
```

## Staff-Level Design Considerations

### WAL-Based CDC
- **Zero impact**: Debezium reads PostgreSQL WAL, not the tables.
- **Staff insight**: Never use trigger-based or polling-based CDC for high-throughput systems. Triggers add latency to every write. Polling (`SELECT * WHERE updated_at > :last`) misses intermediate states and adds read load. WAL-based CDC (Debezium with Logical Decoding) has zero impact on OLTP because it reads the WAL stream, which is written anyway for crash recovery.

### Exactly-Once Processing
- **Idempotent consumers**: Each consumer handles duplicates safely.
- **Staff insight**: Kafka guarantees at-least-once delivery. To achieve exactly-once semantics, make consumers idempotent:
  - Cache invalidation: `DEL` on non-existent key is a no-op.
  - Search index: `index` with same doc_id overwrites — last write wins.
  - Data warehouse: Use `INSERT ... ON CONFLICT DO UPDATE` (upsert).
  
  Combine idempotent consumers with Kafka consumer groups and offset management for exactly-once processing. Don't use Kafka transactions for CDC — they add complexity and reduce throughput.

### Event Ordering
- **Partition key = primary key**: Changes for the same record go to the same partition.
- **Staff insight**: Kafka guarantees ordering within a partition. By setting the partition key to the record's primary key, all changes for the same record (insert → update → delete) are ordered in the same partition. Consumers process events sequentially per partition, so they see changes in the correct order. Cross-partition ordering is not guaranteed — and not needed for per-record processing.

### Schema Evolution Handling
- **Avro + Schema Registry**: Backward-compatible schema changes.
- **Staff insight**: When a column is added to the source table, Debezium publishes the new schema to Schema Registry. Consumers using the latest schema can read both old and new events (Avro defaults handle missing fields). Set Schema Registry compatibility to `BACKWARD` to prevent breaking changes. For consumers that haven't been updated yet, they simply ignore the new field. When a column is dropped, mark it as deprecated in the schema for one cycle before removing.

### Monitoring CDC Lag
- **LSN tracking**: Compare current WAL position with consumer's last processed LSN.
- **Staff insight**: CDC lag is the most important metric. If lag grows, downstream systems have stale data. Monitor:
  - **WAL lag**: `pg_current_wal_lsn() - debezium_last_lsn` in bytes.
  - **Consumer lag**: Kafka consumer group lag per topic.
  - **End-to-end lag**: Time from DB write to cache invalidation.
  
  Alert when WAL lag > 10 seconds (data freshness SLA breach) or consumer lag > 10K messages (backpressure). Common causes of lag: consumer crash, schema incompatibility, or downstream system overload.
