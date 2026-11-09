# SQL vs NoSQL

## Trade-off Overview

Choosing between relational (SQL) and non-relational (NoSQL) databases is one of the most fundamental architectural decisions. There is no universally correct answer — the right choice depends on your data model, access patterns, consistency requirements, and scale.

## SQL (Relational)

### Characteristics
- **Schema**: Fixed schema with tables, rows, columns; enforced constraints.
- **Query language**: SQL — powerful joins, aggregations, subqueries.
- **Consistency**: ACID transactions — strong consistency by default.
- **Scaling**: Vertical scaling; read replicas; sharding (complex).
- **Examples**: PostgreSQL, MySQL, Oracle, SQL Server.

### Pros
- **Data integrity**: Foreign keys, constraints, triggers enforce business rules.
- **Complex queries**: JOINs, window functions, CTEs for analytical queries.
- **ACID**: Full transactional support for financial and critical operations.
- **Mature ecosystem**: Tools, ORMs, monitoring, and talent availability.

### Cons
- **Schema rigidity**: Schema changes require migrations; hard to evolve.
- **Scaling limits**: Vertical scaling has hardware limits; sharding is complex.
- **Write throughput**: Single-node writes limited by disk I/O and locks.

## NoSQL (Non-Relational)

### Characteristics
- **Schema**: Flexible schema — documents, key-value, wide-column, graph.
- **Query language**: Varies by type — limited or no joins.
- **Consistency**: Eventual consistency by default (BASE); some support ACID.
- **Scaling**: Horizontal scaling — designed for distributed deployment.
- **Examples**: MongoDB (document), Cassandra (wide-column), Redis (key-value), Neo4j (graph).

### Pros
- **Horizontal scaling**: Add nodes to increase capacity linearly.
- **Schema flexibility**: Evolve data model without migrations.
- **Write throughput**: Distributed writes scale with cluster size.
- **Specialized models**: Graph for relationships, document for nested data.

### Cons
- **No joins**: Application-level joins or denormalization required.
- **Eventual consistency**: Reads may return stale data.
- **Limited transactions**: Multi-document transactions are limited or expensive.
- **Operational complexity**: Managing distributed clusters is harder than single-node SQL.

## Decision Framework

| Factor | Choose SQL When... | Choose NoSQL When... |
|--------|-------------------|---------------------|
| Data model | Structured, relational, normalized | Unstructured, nested, evolving |
| Queries | Complex joins, aggregations | Simple lookups, key-based access |
| Consistency | Strong consistency required | Eventual consistency acceptable |
| Scale | < 1TB, < 10K RPS | > 1TB, > 10K RPS |
| Transactions | Multi-row ACID required | Single-entity operations |
| Team | SQL expertise available | Distributed systems expertise |

## Staff-Level Insight

> "Use SQL by default. Choose NoSQL only when you have a specific requirement that SQL cannot meet."

- **Polyglot persistence**: Most production systems use **both** — SQL for transactions, NoSQL for caching/search/analytics.
- **Start with SQL**: PostgreSQL supports JSONB, full-text search, and extensions (PostGIS). It covers 80% of "NoSQL use cases."
- **Staff insight**: Don't choose NoSQL for hype. Choose it when you have **proven scaling limits** with SQL. Most startups don't need NoSQL until they hit 10M+ rows and 10K+ RPS. PostgreSQL with proper indexing and read replicas handles most workloads.
