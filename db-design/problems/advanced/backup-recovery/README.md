# Database Backup & Disaster Recovery

## Problem Statement

Design a database backup and disaster recovery strategy for a multi-region deployment. Handle full backups, incremental backups, point-in-time recovery (PITR), cross-region replication, and failover testing. Define RPO (Recovery Point Objective) and RTO (Recovery Time Objective) for different data criticality levels.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Full Backups**: Complete database snapshot at regular intervals.
- **Incremental Backups**: WAL/archive-based continuous backup.
- **Point-in-Time Recovery**: Restore to any second within retention period.
- **Cross-Region Replication**: Async replication to disaster recovery region.
- **Failover**: Automatic or manual failover to standby region.
- **Backup Verification**: Regular restore tests to verify backup integrity.

### Non-Functional Requirements
- **RPO**: < 5 minutes for critical data, < 1 hour for non-critical.
- **RTO**: < 15 minutes for critical data, < 1 hour for non-critical.
- **Retention**: 30 days for PITR, 1 year for monthly snapshots.
- **Encryption**: Backups encrypted at rest and in transit.
- **Testing**: Monthly failover drills to verify RTO/RPO.

## Key Design Decisions

- **Continuous WAL archiving**: For PostgreSQL PITR with near-zero RPO.
- **Cross-region async replication**: For fast failover (low RTO).
- **Automated backup verification**: Weekly restore tests to staging.
- **Chaos engineering**: Quarterly failover drills.
- **Tiered retention**: Daily (30 days), weekly (90 days), monthly (1 year).

## RPO/RTO Matrix

| Data Criticality | RPO | RTO | Strategy |
|-----------------|-----|-----|----------|
| Critical (payments, accounts) | < 1 min | < 5 min | Sync replication + WAL archiving |
| High (orders, users) | < 5 min | < 15 min | Async replication + WAL archiving |
| Medium (products, content) | < 1 hour | < 1 hour | Cross-region async replication |
| Low (analytics, logs) | < 24 hours | < 4 hours | Daily backups + restore from backup |

## Backup Strategy

### PostgreSQL Backup Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Primary Region  │     │   Object Storage  │     │  DR Region      │
│  (US-East)       │────►│  (S3/GCS)        │     │  (US-West)      │
│                  │     │                  │◄────│                 │
│  ┌────────────┐  │     │ • Full backups   │     │  ┌────────────┐ │
│  │ PostgreSQL  │  │────│ • WAL archives   │     │  │ PostgreSQL  │ │
│  │ (Primary)   │  │     │ • Base backups   │     │  │ (Standby)   │ │
│  └────────────┘  │     │ • Binaries       │     │  └────────────┘ │
│                  │     └──────────────────┘     │                 │
│  ┌────────────┐  │                              │                 │
│  │ pgBackRest  │  │     ┌──────────────────┐     │  ┌────────────┐ │
│  │ (Backup)    │  │────►│  Monitoring      │     │  │ Failover    │ │
│  └────────────┘  │     │  (Alerts, Tests)  │     │  │ Controller  │ │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### pgBackRest Configuration

```ini
[global]
repo1-type=s3
repo1-s3-bucket=postgres-backups
repo1-s3-region=us-east-1
repo1-s3-key=***
repo1-s3-key-secret=***
repo1-retention-full=4          # Keep 4 full backups
repo1-retention-diff=7          # Keep 7 differential backups
repo1-retention-archive=30      # Keep 30 days of WAL archives
repo1-crypt-type=aes-256-cbc
repo1-crypt-password=***

[global:archive]
archive-push-ratelimit=50000000  # 50 MB/s WAL archive rate limit

[production]
pg1-path=/var/lib/postgresql/15/data
pg1-port=5432
pg1-socket-path=/var/run/postgresql
```

### PostgreSQL WAL Archiving

```conf
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'pgbackrest archive-push %p'
archive_timeout = 60  # Force WAL switch every 60 seconds

# For cross-region replication
primary_conninfo = 'host=dr-postgres.internal port=5432 user=replicator password=*** application_name=dr_standby'
synchronous_standby_names = ''  # Async for cross-region (low latency)
```

### Backup Schedule

| Type | Frequency | Retention | Storage | RPO Contribution |
|------|-----------|-----------|---------|-----------------|
| Full backup | Daily (2 AM) | 4 weeks | S3 (encrypted) | Base for PITR |
| Differential | Daily (8 AM) | 7 days | S3 (encrypted) | Faster restore |
| WAL archive | Continuous | 30 days | S3 (encrypted) | Near-zero RPO |
| Monthly snapshot | 1st of month | 1 year | S3 Glacier | Long-term retention |

## Point-in-Time Recovery (PITR)

### PITR Process

```bash
# Step 1: Stop the database
systemctl stop postgresql

# Step 2: Restore base backup
pgbackrest restore --stanza=production --type=full

# Step 3: Restore to specific point in time
# Edit recovery.conf (PostgreSQL 12 and earlier)
# Or set restore_command in postgresql.conf (PostgreSQL 13+)

# postgresql.conf for PITR
restore_command = 'pgbackrest archive-get %f %p'
recovery_target_time = '2024-01-15 10:30:00 UTC'
recovery_target_action = 'promote'

# Step 4: Start database — it replays WAL to the target time
systemctl start postgresql

# Step 5: Verify data at target time
SELECT count(*) FROM orders WHERE created_at < '2024-01-15 10:30:00';
```

### Cross-Region Replication Setup

```sql
-- On DR standby (read-only replica)
-- Automatically created via base backup + continuous WAL replay

-- Monitor replication lag
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    EXTRACT(EPOCH FROM (now() - reply_time)) AS lag_seconds
FROM pg_stat_replication;

-- On primary: check WAL send lag
SELECT 
    pg_current_wal_lsn() AS current_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

### Automated Failover

```yaml
# Patroni configuration for automated failover
# /etc/patroni/patroni.yml

namespace: /service/postgres
scope: production-postgres
name: postgres-node-1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 10.0.1.10:8008

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 10.0.1.10:5432
  data_dir: /var/lib/postgresql/15/data
  pg_hba:
    - host all all 0.0.0.0/3 md5
  parameters:
    max_connections: 1000
    shared_buffers: 8GB
    wal_level: replica
    archive_mode: "on"
    archive_command: "pgbackrest archive-push %p"
  create_replica_methods:
    - pgbackrest
    - basebackup
  pgbackrest:
    command: pgbackrest --stanza=production restore
    keep_data: true
    no_params: true

bootstrap:
  cluster_name: production-postgres
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576  # 1MB max lag for failover
    synchronous_mode: false
    postgresql:
      parameters:
        synchronous_standby_names: ""
  initdb:
    - encoding: UTF8
    - data-checksums
  pg_hba:
    - host all all 0.0.0.0/3 md5

tags:
  nofailover: false
  noloadbalance: false
  clonefrom: false
  nosync: false
```

## Backup Verification

### Weekly Restore Test

```bash
#!/bin/bash
# weekly_restore_test.sh
# Runs every Sunday at 3 AM

set -euo pipefail

BACKUP_DATE=$(date -d "yesterday" +%Y-%m-%d)
RESTORE_DIR="/tmp/pg-restore-test-$(date +%Y%m%d)"
TEST_DB="postgres-test-restore"

echo "Starting backup verification for $BACKUP_DATE"

# Restore to temporary directory
pgbackrest restore --stanza=production --type=full \
    --delta --repo=1 --path=$RESTORE_DIR \
    --link-run --log-level-file=debug

# Start temporary instance
initdb -D $RESTORE_DIR/pgdata --username=postgres
pg_ctl -D $RESTORE_DIR/pgdata start

# Run verification queries
psql -h $RESTORE_DIR -d postgres -c "
    -- Check row counts
    SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
    UNION ALL
    SELECT 'orders', COUNT(*) FROM orders
    UNION ALL
    SELECT 'products', COUNT(*) FROM products;
    
    -- Check referential integrity
    SELECT COUNT(*) AS orphan_orders FROM orders 
    WHERE user_id NOT IN (SELECT user_id FROM users);
    
    -- Check data freshness
    SELECT MAX(created_at) AS latest_order FROM orders;
"

# Cleanup
pg_ctl -D $RESTORE_DIR/pgdata stop
rm -rf $RESTORE_DIR

echo "Backup verification completed successfully"
```

### Monitoring & Alerting

```sql
-- Backup monitoring table
CREATE TABLE backup_monitoring (
    backup_id BIGINT PRIMARY KEY,
    backup_type VARCHAR(20) NOT NULL, -- 'full', 'differential', 'wal'
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    size_bytes BIGINT,
    duration_seconds INT,
    status VARCHAR(20) NOT NULL, -- 'running', 'completed', 'failed'
    error_message TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Replication monitoring
CREATE TABLE replication_monitoring (
    check_id BIGINT PRIMARY KEY,
    primary_host VARCHAR(255) NOT NULL,
    standby_host VARCHAR(255) NOT NULL,
    replication_lag_bytes BIGINT,
    replication_lag_seconds DECIMAL(10,2),
    standby_state VARCHAR(20),
    is_wal_archiving BOOLEAN,
    wal_archive_lag_seconds DECIMAL(10,2),
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_replication_time ON replication_monitoring(checked_at DESC);
```

## Staff-Level Design Considerations

### RPO vs RTO Trade-offs
- **RPO (data loss)**: Determined by backup frequency and WAL archiving.
- **RTO (downtime)**: Determined by failover automation and restore speed.
- **Staff insight**: RPO and RTO are independent. You can have low RPO (continuous WAL archiving) with high RTO (manual restore from backup). For low RTO, maintain a warm standby (cross-region replica) that can be promoted in minutes. For low RPO, archive WAL continuously. The cheapest combination: async cross-region replication (low RTO via standby promotion) + WAL archiving (low RPO via PITR).

### Point-in-Time Recovery
- **WAL-based PITR**: Replay Write-Ahead Log to any second.
- **Staff insight**: PITR is your safety net for human errors (accidental DELETE, bad migration). Test PITR regularly — an untested backup is no backup. Use `archive_timeout = 60` to force WAL segment switches every 60 seconds, ensuring at most 60 seconds of data loss. For compliance-critical data, use `synchronous_commit = on` with a synchronous standby for zero RPO.

### Cross-Region Replication
- **Async replication**: DR region follows primary with seconds of lag.
- **Staff insight**: Cross-region sync replication adds 30-100ms latency — unacceptable for most applications. Use async replication to the DR region. The replication lag is your RPO in a failover scenario. Monitor lag continuously and alert when it exceeds your RPO target. For multi-region active-active, use CDC (not replication) to avoid write conflicts.

### Failover Testing
- **Monthly drills**: Test failover procedure in staging; quarterly in production.
- **Staff insight**: An untested failover plan is a guess. Run monthly failover drills:
  1. **Staging**: Full failover test every week on staging environment.
  2. **Production**: Read-only failover test monthly (promote standby, verify, demote).
  3. **Chaos**: Quarterly chaos engineering — kill primary and measure actual RTO.
  
  Document the actual RTO from each drill. If it exceeds the target, improve automation (Patroni, cloud failover groups).

### Backup Encryption & Security
- **Encrypt at rest and in transit**: S3 server-side encryption + TLS for transfer.
- **Staff insight**: Backups contain your entire database — they are a high-value target. Encrypt backups with customer-managed keys (KMS), not service-managed keys. Restrict access to backup storage with IAM policies. Test backup restoration from encrypted backups. For compliance (SOC2, HIPAA), maintain backup access audit logs and implement backup immutability (S3 Object Lock) to prevent ransomware deletion.
