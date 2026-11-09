# Database Design & Data Modeling

This module covers database schema design, data modeling, and storage architecture for staff-level software engineering interviews. Each problem includes comprehensive schema design, indexing strategies, and staff-level production considerations.

**References**: [AlgoMaster](https://algomaster.io/), [Educative.io](https://www.educative.io/), [ByteByteGo](https://bytebytego.com/), [HelloInterview](https://www.hellointerview.com/)

## Contents

- [Relational Schema Design](problems/relational/) — PostgreSQL/MySQL schema design (6 problems)
- [NoSQL Schema Design](problems/nosql/) — Cassandra, DynamoDB, Redis schema design (5 problems)
- [Hybrid Architecture](problems/hybrid/) — OLTP + OLAP + Search hybrid patterns (4 problems)
- [Advanced Topics](problems/advanced/) — Sharding, migration, CDC, consistency, backup (5 problems)

## Relational Schema Design (6 Problems)

| Problem | Key Concepts | Database |
|---------|-------------|----------|
| [E-commerce](problems/relational/ecommerce-schema/) | Products, orders, payments, inventory, reviews | PostgreSQL |
| [Social Network](problems/relational/social-network/) | Users, posts, followers, feeds, notifications | PostgreSQL |
| [Ride-Sharing](problems/relational/ride-sharing/) | Drivers, rides, ratings, surge pricing | PostgreSQL + PostGIS |
| [SaaS Multi-tenancy](problems/relational/saas-multitenancy/) | Tenant isolation, subscriptions, usage | PostgreSQL |
| [Hospital Management](problems/relational/hospital-management/) | Patients, doctors, appointments, billing | PostgreSQL |
| [Content CMS](problems/relational/content-cms/) | Articles, revisions, tags, media, comments | PostgreSQL |

## NoSQL Schema Design (5 Problems)

| Problem | Key Concepts | Database |
|---------|-------------|----------|
| [IoT Time-Series](problems/nosql/iot-timeseries/) | Sensor data, aggregations, retention | Cassandra/InfluxDB |
| [Real-time Chat](problems/nosql/realtime-chat/) | Messages, conversations, read receipts | Cassandra/DynamoDB |
| [Session Store](problems/nosql/session-store/) | Distributed sessions, TTL, clustering | Redis |
| [Product Catalog](problems/nosql/product-catalog/) | High-read catalog, denormalization | Cassandra/DynamoDB |
| [Clickstream Analytics](problems/nosql/clickstream-analytics/) | Event ingestion, real-time dashboards | Cassandra + Kafka |

## Hybrid Architecture (4 Problems)

| Problem | Key Concepts | Stack |
|---------|-------------|-------|
| [Analytics Pipeline](problems/hybrid/analytics-pipeline/) | OLTP → streaming → OLAP | PostgreSQL → Kafka → ClickHouse |
| [Search Engine](problems/hybrid/search-engine/) | Full-text search, index sync | PostgreSQL → Elasticsearch |
| [Recommendation System](problems/hybrid/recommendation-system/) | Two-phase rec, feature store | PostgreSQL + Cassandra + Redis |
| [Log Aggregation](problems/hybrid/log-aggregation/) | Log collection, indexing, alerting | Fluentd → Kafka → Elasticsearch |

## Advanced Topics (5 Problems)

| Problem | Key Concepts |
|---------|-------------|
| [Sharding Strategy](problems/advanced/sharding-strategy/) | Shard key, rebalancing, cross-shard queries, virtual nodes |
| [Data Migration](problems/advanced/data-migration/) | Zero-downtime migration, dual-write, CDC, reconciliation |
| [CDC Pipeline](problems/advanced/cdc-pipeline/) | Change capture, event streaming, schema evolution, exactly-once |
| [Consistency Models](problems/advanced/consistency-models/) | CAP, PACELC, quorum, causal consistency, vector clocks |
| [Backup & Recovery](problems/advanced/backup-recovery/) | RPO/RTO, PITR, cross-region DR, failover testing |

## How to Use

1. **Start with relational**: Master normalized schema design with PostgreSQL
2. **Learn NoSQL patterns**: Understand when and how to use document, wide-column, and key-value stores
3. **Study hybrid architectures**: Combine OLTP, OLAP, and search for real-world systems
4. **Master advanced topics**: Sharding, migration, CDC, and consistency for staff-level depth
5. **Practice schema design**: Given a system requirement, design the schema, indexes, and access patterns
