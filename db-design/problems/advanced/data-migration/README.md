# Zero-Downtime Data Migration Strategy

## Problem Statement

Design a zero-downtime data migration strategy for migrating from MySQL to PostgreSQL (or from a monolith database to microservices databases). Handle schema differences, data transformation, dual-write pattern, data validation and reconciliation, cutover strategy, and rollback plan.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Schema Mapping**: Convert MySQL schema to PostgreSQL (data types, constraints, functions).
- **Data Transformation**: Convert data formats (datetime, JSON, enums, boolean).
- **Dual-Write**: Write to both source and target during migration window.
- **Backfill**: Migrate historical data from source to target.
- **Validation**: Verify data consistency between source and target.
- **Cutover**: Switch reads from source to target with zero downtime.
- **Rollback**: Revert to source if issues are detected.

### Non-Functional Requirements
- **Zero downtime**: Application remains available throughout migration.
- **Data consistency**: No data loss or corruption during migration.
- **Performance**: Migration does not degrade production performance.
- **Idempotency**: Migration can be retried without side effects.
- **Monitoring**: Real-time migration progress and lag tracking.

## Key Design Decisions

- **Dual-write pattern**: Write to both databases during transition period.
- **CDC for backfill**: Debezium captures changes during backfill for incremental sync.
- **Feature flag for reads**: Gradual read cutover via percentage-based routing.
- **Data reconciliation**: Checksums and row counts for validation.
- **Rollback via dual-write**: Since we're still writing to source, rollback is instant.

## Migration Phases

```
Phase 1: Preparation (1-2 weeks)
├─ Design target schema (PostgreSQL)
├─ Build data transformation layer
├─ Set up dual-write infrastructure
└─ Create validation tools

Phase 2: Dual-Write (1 week)
├─ Deploy dual-write to production
├─ Start writing to both source and target
└─ Monitor for write errors

Phase 3: Backfill (1-2 weeks)
├─ Migrate historical data in batches
├─ CDC captures changes during backfill
└─ Validate backfilled data

Phase 4: Read Cutover (1 week)
├─ Route 1% of reads to target
├─ Gradually increase: 5% → 25% → 50% → 100%
├─ Compare results between source and target
└─ Monitor latency and error rates

Phase 5: Completion
├─ Stop dual-write (write to target only)
├─ Archive source database
└─ Remove migration infrastructure
```

## Schema Design

### Source Schema (MySQL)

```sql
-- MySQL source
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    status ENUM('active', 'suspended', 'deleted') DEFAULT 'active',
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id)
) ENGINE=InnoDB;
```

### Target Schema (PostgreSQL)

```sql
-- PostgreSQL target
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id, created_at DESC);
```

### Migration Tracking Table

```sql
-- Track migration progress
CREATE TABLE migration_tracking (
    table_name VARCHAR(100) PRIMARY KEY,
    last_migrated_id BIGINT DEFAULT 0,
    last_migrated_at TIMESTAMP,
    total_rows BIGINT,
    migrated_rows BIGINT,
    is_complete BOOLEAN DEFAULT FALSE,
    error_count BIGINT DEFAULT 0,
    last_error_message TEXT
);
```

### Data Reconciliation Table

```sql
CREATE TABLE reconciliation_results (
    check_id BIGINT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    source_count BIGINT NOT NULL,
    target_count BIGINT NOT NULL,
    source_checksum VARCHAR(64),
    target_checksum VARCHAR(64),
    is_consistent BOOLEAN NOT NULL,
    checked_at TIMESTAMP DEFAULT NOW()
);
```

## Implementation

### Dual-Write Layer (Pseudocode)

```python
class DualWriteRepository:
    def __init__(self, source_db, target_db, migration_config):
        self.source = source_db
        self.target = target_db
        self.config = migration_config
    
    def save_user(self, user):
        # Always write to source first (source of truth)
        self.source.execute("INSERT INTO users ...", user)
        
        # Write to target (best effort)
        if self.config.dual_write_enabled:
            try:
                transformed = self.transform_user(user)
                self.target.execute("INSERT INTO users ...", transformed)
            except Exception as e:
                # Log error but don't fail the request
                self.log_migration_error("users", user.id, str(e))
                # Will be caught by backfill/CDC later
    
    def get_user(self, user_id):
        # Read routing based on feature flag
        if self.should_read_from_target(user_id):
            result = self.target.execute("SELECT * FROM users WHERE id = %s", user_id)
            if self.config.compare_mode and random() < 0.01:
                # 1% shadow read for validation
                source_result = self.source.execute("SELECT * FROM users WHERE id = %s", user_id)
                self.compare_results(result, source_result)
            return result
        else:
            return self.source.execute("SELECT * FROM users WHERE id = %s", user_id)
```

### Backfill Script (Pseudocode)

```python
def backfill_table(table_name, batch_size=10000):
    tracking = get_migration_tracking(table_name)
    last_id = tracking.last_migrated_id
    
    while True:
        # Read batch from source
        rows = source.execute(
            f"SELECT * FROM {table_name} WHERE id > %s ORDER BY id LIMIT %s",
            last_id, batch_size
        )
        
        if not rows:
            break
        
        # Transform and write to target
        for row in rows:
            transformed = transform_row(table_name, row)
            target.execute(f"INSERT INTO {table_name} ... ON CONFLICT DO UPDATE", transformed)
            last_id = row.id
        
        # Update tracking
        update_migration_tracking(table_name, last_id, len(rows))
        
        # Throttle to avoid impacting production
        time.sleep(config.backfill_delay_ms / 1000)
    
    mark_table_complete(table_name)
```

### CDC Configuration (Debezium)

```json
{
  "name": "mysql-to-postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql-source.internal",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "***",
    "database.server.id": "5401",
    "database.server.name": "mysql_source",
    "database.include.list": "app_db",
    "table.include.list": "app_db.users,app_db.orders",
    "topic.prefix": "mysql",
    "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
    "schema.history.internal.kafka.topic": "schema_history"
  }
}
```

## Staff-Level Design Considerations

### Dual-Write Pattern
- **Source-first writes**: Source DB is the source of truth during migration.
- **Staff insight**: Always write to source first. If source write succeeds and target write fails, the CDC/backfill process will catch up. Never write to target first — if target succeeds and source fails, you lose data. Dual-write adds latency (~5-10ms) — communicate this to stakeholders and consider async target writes for latency-sensitive paths.

### CDC for Incremental Sync
- **Debezium captures changes**: During backfill, CDC captures new changes to a Kafka topic.
- **Staff insight**: Backfill and CDC run concurrently. Backfill migrates historical data in batches; CDC captures new changes. After backfill completes, replay the CDC events to apply any changes that occurred during backfill. This ensures zero data loss. Use Kafka's offset tracking to know exactly which events have been applied.

### Read Cutover Strategy
- **Percentage-based routing**: Gradually shift reads from source to target.
- **Staff insight**: Use a feature flag with percentage routing: `if (hash(user_id) % 100 < target_percentage) read_from_target()`. Start at 1% and monitor for errors. Compare results between source and target for the shadow reads (1% of traffic). If error rate is < 0.1%, increase to 5%, then 25%, 50%, 100%. This gradual approach catches schema mismatches and data transformation bugs early.

### Data Reconciliation
- **Checksums and counts**: Verify row counts and data checksums per table.
- **Staff insight**: After backfill, run reconciliation: compare row counts, sum of numeric columns, and hash of all data. Use `SELECT COUNT(*), SUM(amount), MD5(GROUP_CONCAT(id ORDER BY id))` for each table. Automate this as a nightly job during migration. Any discrepancy triggers an alert and pauses the read cutover.

### Rollback Plan
- **Instant rollback**: Since source still receives writes, rollback is a feature flag toggle.
- **Staff insight**: The dual-write pattern makes rollback trivial — switch the read routing flag back to 100% source. No data is lost because source has all writes. The only risk is writes that succeeded on target but failed on source during the brief dual-write window — these are caught by the error logging and can be manually replayed. Always keep the source database running and writable until migration is fully verified (at least 1 week after 100% cutover).
