# Log Aggregation Hybrid Database Architecture

## Problem Statement

Design a hybrid database architecture for a log aggregation system (like ELK stack) that collects logs from distributed services, indexes them for search, and provides dashboards and alerting. Handle log parsing, index rotation, retention policies, and hot-warm-cold tiering for cost optimization.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Log Collection**: Agents (Fluentd/Filebeat) ship logs from all services.
- **Log Parsing**: Extract structured fields from raw log lines (JSON, regex).
- **Indexing**: Elasticsearch indexes logs for full-text search and filtering.
- **Dashboards**: Kibana/Grafana for log visualization and metrics.
- **Alerting**: Pattern-based alerts (e.g., error rate > 5%, specific error messages).
- **Retention**: Hot (7 days), warm (30 days), cold (90 days), delete after 1 year.

### Non-Functional Requirements
- **Throughput**: 100K log events/second ingestion.
- **Search latency**: < 1 second for log queries.
- **Cost optimization**: Hot-warm-cold tiering reduces storage cost by 70%.
- **Reliability**: No log loss during agent or indexer outage.
- **PII redaction**: Automatically mask sensitive data in logs.

## Key Design Decisions

- **Fluentd for collection**: Reliable buffering, retry, and routing.
- **Kafka as buffer**: Decouples collectors from indexers; handles burst traffic.
- **Elasticsearch for search**: Full-text search, aggregations, dashboards.
- **Hot-warm-cold architecture**: Fast SSD for recent logs, HDD for older logs.
- **Index lifecycle management (ILM)**: Automated rollover, shrink, and delete.

## Architecture

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────────┐
│ Services │───►│ Fluentd/ │───►│  Kafka   │───►│ Log Indexer   │
│ (Apps)   │    │ Filebeat │    │ (Buffer) │    │ (Consumer)    │
└──────────┘    └──────────┘    └──────────┘    └───────┬───────┘
                                                         │
                                          ┌──────────────┤
                                          ▼              ▼
                                   ┌────────────┐  ┌───────────────┐
                                   │ Elasticsearch│  │  Kibana/     │
                                   │ (Hot-Warm-  │  │  Grafana      │
                                   │  Cold)      │  │ (Dashboards)  │
                                   └────────────┘  └───────────────┘
                                          │
                                          ▼
                                   ┌────────────┐
                                   │  Alerting  │  ← Pattern matching, thresholds
                                   │  Engine    │
                                   └────────────┘
```

## Schema Design

### Log Event Format (JSON)

```json
{
  "@timestamp": "2024-01-15T10:30:00.123Z",
  "level": "ERROR",
  "service": "order-service",
  "host": "ip-10-0-1-5.ec2.internal",
  "environment": "production",
  "message": "Failed to process order: timeout connecting to payment gateway",
  "trace_id": "abc123def456",
  "span_id": "span789",
  "request_id": "req-12345",
  "user_id": "user-67890",
  "metadata": {
    "method": "POST",
    "path": "/api/v1/orders",
    "status_code": 500,
    "duration_ms": 30000,
    "error_type": "ConnectionTimeout",
    "stack_trace": "..."
  }
}
```

### Elasticsearch Index Template

```json
PUT _index_template/log_template
{
  "index_patterns": ["logs-*"],
  "data_stream": {},
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "log_ilm_policy",
      "index.lifecycle.rollover_alias": "logs"
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "level": { "type": "keyword" },
        "service": { "type": "keyword" },
        "host": { "type": "keyword" },
        "environment": { "type": "keyword" },
        "message": { "type": "text" },
        "trace_id": { "type": "keyword" },
        "span_id": { "type": "keyword" },
        "request_id": { "type": "keyword" },
        "user_id": { "type": "keyword" },
        "metadata": { "type": "flattened" }
      }
    }
  }
}
```

### ILM Policy (Index Lifecycle Management)

```json
PUT _ilm/policy/log_ilm_policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d",
            "max_docs": 10000000
          },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "allocate": {
            "number_of_replicas": 1,
            "require": { "data": "warm" }
          },
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "allocate": {
            "number_of_replicas": 0,
            "require": { "data": "cold" }
          },
          "set_priority": { "priority": 0 }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

### Alerting Rules (PostgreSQL)

```sql
CREATE TABLE alert_rules (
    rule_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    query VARCHAR(500) NOT NULL, -- ES query DSL
    condition VARCHAR(50) NOT NULL, -- 'count_gt', 'percentage_gt', 'pattern_match'
    threshold DECIMAL(10,2) NOT NULL,
    window_minutes INT NOT NULL, -- Evaluation window
    severity VARCHAR(20) NOT NULL, -- 'info', 'warning', 'critical'
    channels TEXT[], -- ['slack', 'pagerduty', 'email']
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alert_history (
    alert_id BIGINT PRIMARY KEY,
    rule_id UUID NOT NULL,
    triggered_at TIMESTAMP DEFAULT NOW(),
    matched_count BIGINT,
    sample_messages TEXT[],
    resolved_at TIMESTAMP,
    acknowledged_by BIGINT,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(rule_id)
);

CREATE INDEX idx_alert_history_rule ON alert_history(rule_id, triggered_at DESC);
```

### Kafka Topics

```
# Raw log events from Fluentd/Filebeat
Topic: logs.raw
Partition key: service
Schema: JSON
Retention: 3 days
Partitions: 50
Replication: 3

# Parsed and enriched logs
Topic: logs.parsed
Partition key: service
Schema: JSON
Retention: 1 day
Partitions: 50

# Alert events
Topic: alerts.triggered
Partition key: rule_id
Schema: JSON
Retention: 30 days
Partitions: 10
```

### Fluentd Configuration

```xml
# Input: Collect logs from files
<source>
  @type tail
  path /var/log/services/*.log
  pos_file /var/log/fluend/*.log.pos
  tag service.*
  <parse>
    @type json
    time_key @timestamp
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

# Filter: PII redaction
<filter service.**>
  @type record_transformer
  <record>
    user_id ${record["user_id"] ? "REDACTED" : nil}
    email ${record["email"] ? "REDACTED" : nil}
  </record>
</filter>

# Output: Buffer to Kafka
<match service.**>
  @type kafka2
  brokers kafka-1:9092,kafka-2:9092,kafka-3:9092
  default_topic logs.raw
  <format>
    @type json
  </format>
  <buffer>
    @type file
    path /var/log/fluentd/buffer
    flush_interval 5s
    chunk_limit_size 8m
    total_limit_size 1g
    retry_max_interval 30
    retry_forever true
  </buffer>
</match>
```

## Staff-Level Design Considerations

### Log Volume Management
- **Index rollover**: New index every day or when size exceeds 50GB.
- **Staff insight**: Never use a single index for all logs — it grows unbounded and degrades search performance. Use time-based index rollover (daily) with ILM policy. Each index stays under 50GB for optimal shard performance. The alias `logs` always points to the current write index.

### Hot-Warm-Cold Tiering
- **Hot**: SSD nodes for recent 7 days (frequent search, high IOPS).
- **Warm**: HDD nodes for 7-30 days (occasional search, read-optimized).
- **Cold**: Cold storage for 30-90 days (rare search, no replicas).
- **Staff insight**: Hot-warm-cold tiering reduces storage cost by 70% because 90% of log queries are for the last 7 days. Use Elasticsearch node attributes (`data: hot`, `data: warm`, `data: cold`) and ILM allocate actions to move indices automatically.

### Structured vs Unstructured Logging
- **Structured (JSON)**: Application logs emitted as JSON with predefined fields.
- **Unstructured**: Syslog, nginx access logs — require Grok parsing.
- **Staff insight**: Mandate structured logging (JSON) for all services. It eliminates parsing overhead in Fluentd and enables direct field-level queries in Elasticsearch. For unstructured logs (3rd party, system), use Grok patterns in Fluentd to extract fields before indexing.

### PII Redaction in Logs
- **Filter at ingestion**: Fluentd filter removes sensitive fields before Kafka.
- **Staff insight**: Never rely on application-level PII redaction alone — developers forget. Add a Fluentd filter as a safety net that masks known PII fields (email, phone, ssn, credit_card). Use Elasticsearch's `ignore_above` mapping for fields that shouldn't be searched (e.g., stack traces) to save storage.

### Alerting on Log Patterns
- **Window-based evaluation**: Count errors in last 5 minutes; alert if > threshold.
- **Staff insight**: Don't alert on every error — it causes alert fatigue. Use windowed aggregation: "if error rate > 5% over 5 minutes, alert." Use Elasticsearch's Watcher or a separate alerting engine (e.g., Alerta, PagerDuty) that queries the log index on a schedule. For real-time alerting, use Kafka Streams to count error events per window and trigger alerts on threshold breach.
