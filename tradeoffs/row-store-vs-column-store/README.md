# Row-store vs Column-store

## Trade-off Overview

Row-store databases (PostgreSQL, MySQL) store data row-by-row, optimized for OLTP. Column-store databases (ClickHouse, Redshift, Snowflake) store data column-by-column, optimized for OLAP analytics.

## Row-store (OLTP)
- **Pros**: Fast point lookups, efficient writes, ACID transactions.
- **Cons**: Slow analytical queries scanning many columns.
- **Use when**: Transactional workloads, CRUD operations, real-time queries.

## Column-store (OLAP)
- **Pros**: Fast aggregations, compression (10x), scan only needed columns.
- **Cons**: Slow point lookups, expensive writes, no transactions.
- **Use when**: Analytics, reporting, dashboards, large-scale aggregations.

## Staff-Level Insight

> "Use row-store for transactions, column-store for analytics. Sync via CDC."

- **Staff insight**: Never run analytical queries on your OLTP database. Use **CDC (Debezium)** to sync from PostgreSQL (row-store) to ClickHouse/Redshift (column-store). This keeps your transactional DB fast while enabling complex analytics.
