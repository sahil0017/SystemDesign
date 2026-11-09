# Normalization vs Denormalization

## Trade-off Overview

Normalization reduces data redundancy through relational structure; denormalization improves read performance by duplicating data. The choice affects write complexity, read speed, and storage cost.

## Normalization

### Pros
- **No redundancy**: Each fact stored once; no update anomalies.
- **Data integrity**: Foreign keys and constraints enforce consistency.
- **Storage efficiency**: Less duplicate data means smaller storage.

### Cons
- **Complex reads**: Multiple JOINs slow down queries.
- **Write-heavy friendly**: Updates touch fewer rows.

## Denormalization

### Pros
- **Fast reads**: No JOINs needed; all data in one table.
- **Simplified queries**: Single-table lookups are faster and simpler.
- **Analytics friendly**: Pre-joined data for reporting.

### Cons
- **Data redundancy**: Same data stored in multiple places.
- **Update anomalies**: Must update all copies to maintain consistency.
- **Storage cost**: More duplicate data means larger storage.

## Decision Framework

| Factor | Choose Normalization When... | Choose Denormalization When... |
|--------|-----------------------------|-------------------------------|
| Read/Write ratio | Write-heavy system | Read-heavy system |
| Query complexity | Simple queries, few JOINs | Complex queries, many JOINs |
| Consistency | Must be consistent at all times | Eventual consistency acceptable |
| Storage | Storage is expensive | Storage is cheap |

## Staff-Level Insight

> "Normalize for writes, denormalize for reads. Most production systems do both."

- **Write normalized, read denormalized**: Store in normalized tables; sync to denormalized read models via events.
- **Staff insight**: Use **CQRS** — normalized write model for ACID integrity, denormalized read model for fast queries. Sync via Kafka events. This gives you the best of both: correct writes and fast reads. Don't denormalize your primary database — create separate read-optimized tables.
