# Distributed File Storage

## Problem Statement

Design a distributed object storage system (like Amazon S3 or Google Cloud Storage) that stores and retrieves unstructured data (files, images, videos) at petabyte scale. The system must support multipart upload, versioning, lifecycle policies, CDN integration, and high durability with eventual consistency.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Object operations**: Put, Get, Delete, List objects with metadata.
- **Multipart upload**: Split large files into chunks for parallel upload and resume.
- **Versioning**: Keep multiple versions of an object; restore previous versions.
- **Lifecycle policies**: Auto-transition objects between storage tiers (hot → warm → cold → archive).
- **Presigned URLs**: Generate time-limited URLs for direct client access.
- **CDN integration**: Cache frequently accessed objects at edge locations.
- **Replication**: Cross-region replication for disaster recovery.

### Non-Functional Requirements
- **Durability**: 99.999999999% (11 nines) — erasure coding or multi-replica.
- **Availability**: 99.99% for read operations.
- **Throughput**: Handle 100K uploads/second and 1M downloads/second.
- **Scalability**: Store petabytes of data across multiple regions.

## Key Design Decisions
- **Erasure coding**: Split objects into data + parity chunks for durability with lower storage cost.
- **Consistent hashing**: Distribute objects across storage nodes using hash ring.
- **Multipart upload**: Client uploads chunks in parallel; server merges on completion.
- **Tiered storage**: Hot (SSD), warm (HDD), cold (tape/archive) based on access patterns.

## Architecture

```
Client
   |
   +-- API Gateway --> Metadata Service --> Object Store Cluster
   |                         |                    |
   |                         |                    +-- Node A (Chunks)
   |                         |                    +-- Node B (Chunks)
   |                         |                    +-- Node C (Chunks)
   |                         |
   |                         +-- Lifecycle Manager --> Tiered Storage
   |                                                    |
   |                                                    +-- Hot (SSD)
   |                                                    +-- Warm (HDD)
   |                                                    +-- Cold (Archive)
   |
   +-- CDN (Edge Cache) --> Origin Pull --> Object Store
```

## Staff-Level Design Considerations

### Erasure Coding vs Replication
- **Replication (3x)**: Store 3 full copies — simple, fast reads, 3x storage cost.
- **Erasure coding (4+2)**: Split into 4 data + 2 parity chunks — 1.5x storage cost, can lose 2 nodes.
- **Staff insight**: Use **replication for hot data** (fast reads, simpler recovery) and **erasure coding for cold data** (cost savings matter more than read speed). S3 uses this hybrid approach — standard storage is replicated, infrequent access uses erasure coding.

### Multipart Upload Design
- **Chunk size**: 5MB minimum, 5GB maximum per part; upload parts in parallel.
- **Part numbering**: Parts numbered 1-N; server validates all parts before merge.
- **Abort handling**: Clean up orphaned parts after configurable timeout (7-365 days).
- **Staff insight**: Use **adaptive chunk size** — for files < 100MB, use single upload. For 100MB-5GB, use 100MB chunks. For > 5GB, use 1GB chunks. This balances parallelism overhead with network efficiency. Track upload sessions in metadata DB for resume capability.

### Metadata Management
- **Separate metadata store**: Store object metadata (size, content-type, tags) in a distributed DB.
- **Metadata vs data**: Metadata is small and frequently accessed; data is large and less frequently accessed.
- **Staff insight**: **Never co-locate metadata with object data**. Metadata queries (list, search by tag) should hit a fast metadata store (DynamoDB/Cassandra), not scan storage nodes. Object data is accessed by key; metadata is queried by many dimensions.

### Consistency Model
- **Eventual consistency**: After write, reads may return stale data for up to 15 minutes.
- **Read-after-write**: Strong consistency for the writer's subsequent reads.
- **Staff insight**: S3 moved to **strong consistency by default** in 2020. Use strong consistency for new systems. Eventual consistency was a historical limitation of multi-region replication; modern systems (Spanner, CockroachDB) provide strong consistency with global replication at acceptable latency.

### Lifecycle Management
- **Access tracking**: Track last access time for each object to determine tier.
- **Transition policies**: Auto-move objects based on age or access frequency.
- **Staff insight**: Use **access-tiering** — automatically move objects between tiers based on access patterns. Objects not accessed in 30 days → warm. Not accessed in 90 days → cold. Not accessed in 1 year → archive. This reduces storage costs by 60-80% without manual management.
