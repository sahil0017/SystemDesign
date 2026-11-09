# Designing Data-Intensive Applications by Martin Kleppmann

## Summary

The definitive guide to data systems architecture. Covers how modern databases, storage engines, and distributed systems work under the hood — from B-trees to LSM trees, from replication to partitioning, from batch to stream processing.

## Key Chapters

1. **Relational Database Foundations**: ACID, SQL, indexes, query optimization
2. **Data Modeling**: Relational vs document models, schema evolution
3. **Encoding and Serialization**: JSON, Avro, Protocol Buffers, MessagePack
4. **Storage and Retrieval**: B-trees, LSM trees, columnar storage, vector databases
5. **Replication**: Primary-backup, multi-primary, conflict-free replicated data types (CRDTs)
6. **Partitioning**: Sharding, range/hash/dirty partitioning, rebalancing
7. **Transactions**: Isolation levels, serializability, two-phase commit
8. **Distributed Data**: Consensus (Paxos, Raft), CAP theorem, vector clocks
9. **Batch Processing**: MapReduce, Spark, data lakes
10. **Stream Processing**: Kafka, Flink, event-time processing, windowing

## Key Takeaways

- **There are no silver bullets**: Every data system involves trade-offs between consistency, availability, latency, and throughput
- **Understand your data access patterns**: Choose storage engines based on how you read and write data
- **Design for failure**: Assume anything can fail at any time — design systems that degrade gracefully
- **Data is the most important asset**: Design data models and pipelines that are easy to migrate and evolve

## Why Read This Book

- Best single book for understanding the "why" behind system design decisions
- Required reading for any staff engineer working with data systems
- Bridges the gap between academic distributed systems theory and production practice

## Related Problems in This Repository

- [DB Design - Relational](../../db-design/problems/relational-ecommerce/)
- [DB Design - NoSQL](../../db-design/problems/nosql-iot-timeseries/)
- [HLD - Database Sharding](../../hld/fundamentals/database-sharding.md)
- [Trade-offs - SQL vs NoSQL](../../tradeoffs/sql-vs-nosql/)
