# Notification System - Database Design

## Database Strategy

- **PostgreSQL**: User preferences, templates, notification definitions (ACID)
- **Cassandra**: Delivery logs, analytics events (high write throughput)
- **Redis**: Preference cache, rate limiting, deduplication, in-app notifications

## PostgreSQL Schema

### User Preferences
```sql
CREATE TABLE user_preferences (
    user_id BIGINT PRIMARY KEY,
    push_enabled BOOLEAN DEFAULT TRUE,
    email_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    email_frequency VARCHAR(20) DEFAULT 'instant', -- 'instant', 'daily', 'weekly'
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Templates
```sql
CREATE TABLE templates (
    template_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    channel VARCHAR(20) NOT NULL, -- 'push', 'email', 'sms', 'in-app'
    subject_template TEXT,
    body_template TEXT NOT NULL,
    variables JSONB, -- List of expected variables
    locales JSONB, -- Translations: {"en": {...}, "es": {...}}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_templates_channel ON templates(channel, is_active);
```

### Scheduled Notifications
```sql
CREATE TABLE scheduled_notifications (
    schedule_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    template_id BIGINT NOT NULL,
    channel VARCHAR(20) NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    variables JSONB,
    metadata JSONB,
    scheduled_for TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'failed', 'cancelled'
    recurrence VARCHAR(50), -- Cron expression or NULL
    last_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (template_id) REFERENCES templates(template_id)
);

CREATE INDEX idx_scheduled_status ON scheduled_notifications(status, scheduled_for);
CREATE INDEX idx_scheduled_user ON scheduled_notifications(user_id, status);
```

### In-App Notifications
```sql
CREATE TABLE in_app_notifications (
    notification_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(200),
    body TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_inapp_user ON in_app_notifications(user_id, is_read, created_at DESC);
CREATE INDEX idx_inapp_expires ON in_app_notifications(expires_at) WHERE expires_at IS NOT NULL;
```

## Cassandra Schema (Delivery Logs)

### Delivery Events
```sql
CREATE TABLE delivery_events (
    notification_id UUID,
    created_at TIMESTAMP,
    event_type TEXT, -- 'sent', 'delivered', 'opened', 'clicked', 'failed'
    channel TEXT,
    user_id BIGINT,
    template_id BIGINT,
    provider TEXT, -- 'fcm', 'apns', 'ses', 'twilio'
    provider_id TEXT,
    error_message TEXT,
    metadata MAP<TEXT, TEXT>,
    PRIMARY KEY (notification_id, created_at, event_type)
) WITH CLUSTERING ORDER BY (created_at ASC);
```

### User Delivery Stats (Materialized)
```sql
CREATE TABLE user_delivery_stats (
    user_id BIGINT,
    month TEXT, -- '2024-01'
    channel TEXT,
    sent_count BIGINT,
    delivered_count BIGINT,
    opened_count BIGINT,
    clicked_count BIGINT,
    failed_count BIGINT,
    PRIMARY KEY ((user_id, month), channel)
);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `pref:{user_id}` | Hash | User preference cache | 5min |
| `rate:{user_id}:{channel}` | String | Per-user rate limit counter | 1h |
| `rate:global:{channel}` | String | Global rate limit counter | 1min |
| `dedup:{notification_id}` | String | Send deduplication | 24h |
| `inapp:{user_id}` | Sorted Set | In-app notifications (score=timestamp) | No TTL |
| `template:{template_id}` | String | Template cache | 1h |
| `quiet:{user_id}` | String | Quiet hours flag | 1h |

## Indexes Strategy

### PostgreSQL Indexes
- **Scheduled notifications**: Composite index on `(status, scheduled_for)` for polling pending jobs
- **In-app notifications**: Composite index on `(user_id, is_read, created_at DESC)`
- **Expiry cleanup**: Partial index on `expires_at` for cleanup worker

### Cassandra Partition Strategy
- **Delivery events**: Partition by `notification_id` for full event timeline
- **User stats**: Partition by `(user_id, month)` for monthly aggregation
- **Compaction**: SizeTieredCompaction for time-series data

## Staff-Level Database Considerations

### Delivery Log Retention
- **Hot data**: 30 days in Cassandra for real-time analytics
- **Warm data**: 90 days in compressed format
- **Cold data**: Archive to S3 Glacier for compliance
- **Staff insight**: Use **TTL-based auto-expiration** in Cassandra for hot data cleanup

### Rate Limiting Storage
- **Redis**: Atomic INCR with EXPIRE for sliding window rate limiting
- **Fallback**: If Redis is down, allow notifications (fail open) to avoid blocking critical alerts
- **Staff insight**: Use **Redis Lua script** for atomic check-and-increment to prevent race conditions

### Template Versioning
- **Soft delete**: Mark templates as inactive instead of deleting
- **Version tracking**: Store template history for audit and rollback
- **Staff insight**: Use **JSONB** in PostgreSQL for flexible template variables without schema changes
