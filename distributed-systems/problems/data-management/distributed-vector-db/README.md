# Distributed Vector Database

## Problem Statement

Design a distributed vector database that stores and queries high-dimensional embeddings with approximate nearest neighbor (ANN) search, supporting horizontal scaling, replication, metadata filtering, and hybrid search for AI/ML workloads.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Vector storage**: Store high-dimensional vectors (128-4096 dimensions) with associated metadata.
- **ANN search**: HNSW/IVF-PQ based approximate nearest neighbor search with configurable recall.
- **Metadata filtering**: Filter vectors by metadata fields during search (e.g., tenant_id, category).
- **Hybrid search**: Combine vector similarity with keyword search (BM25) on text fields.
- **CRUD operations**: Insert, update, delete vectors with versioning.
- **Replication**: Multi-replica storage for fault tolerance and read scaling.
- **Sharding**: Horizontal partitioning of vectors across nodes for write scaling.

### Non-Functional Requirements
- **Scale**: 10B+ vectors; 10K+ queries per second; 100K+ inserts per second.
- **Latency**: ANN search < 100ms (p95); insert < 10ms.
- **Recall**: > 95% recall at top-10 results with HNSW indexing.
- **Availability**: 99.9% uptime with automatic failover.

## Key Design Decisions
- **Index type**: HNSW for high recall; IVF-PQ for memory efficiency at scale.
- **Sharding strategy**: Hash-based sharding on vector ID with virtual nodes for rebalancing.
- **Replication**: Synchronous replication for writes; asynchronous for reads.
- **Query routing**: Broadcast queries to all shards; merge and re-rank results centrally.

## Architecture Overview

```
Client → Query Router → Shard 1 (HNSW Index) → Top-K Results
                       → Shard 2 (HNSW Index) → Top-K Results
                       → Shard N (HNSW Index) → Top-K Results
                       → Merge & Re-rank → Final Results
Insert → Shard Assigner → Shard N → Index Update → Replicas
```

## Staff-Level Design Considerations

### Index Selection
- **HNSW**: Best recall (95%+), O(log n) search, but high memory usage (2-3x vector size).
- **IVF-PQ**: Lower recall (85-90%), but 10x memory compression with Product Quantization.
- **Staff insight**: Use HNSW for < 100M vectors where recall matters. Use IVF-PQ for > 100M vectors where memory cost is a concern. Many systems use a hybrid: HNSW for hot data, IVF-PQ for cold data.

### Sharding Strategy
- **Hash-based**: Shard by hash(vector_id) % num_shards. Simple and uniform distribution.
- **Virtual nodes**: Each physical shard owns multiple virtual nodes for fine-grained rebalancing.
- **Staff insight**: ANN search doesn't support true distributed search — you must search all shards and merge results. Use virtual nodes (like DynamoDB) for smooth rebalancing when adding/removing shards.

### Query Processing
- **Broadcast**: Send queries to all shards in parallel; each shard returns top-K.
- **Merge**: Collect all shard results; re-rank by distance; return global top-K.
- **Staff insight**: The merge step is the bottleneck. Use a top-K heap (priority queue) for O(N log K) merging where N = number of shards. For 100 shards and K=10, that's 100 × log(10) = 332 operations.

### Metadata Filtering
- **Inverted index**: Build an inverted index on metadata fields for fast filtering.
- **Filter-then-search**: Intersect filter results with ANN results for filtered search.
- **Staff insight**: Metadata filtering is the hardest part of vector DBs. A naive approach (filter after ANN search) loses recall. Use an inverted index to pre-filter candidates before ANN search, or use a hybrid approach (ANN search + post-filter with larger K).

### Replication and Consistency
- **Leader-follower**: One leader per shard handles writes; followers replicate asynchronously.
- **Read from followers**: Route read queries to any replica for load distribution.
- **Staff insight**: Vector DBs are eventually consistent by nature. ANN search is approximate, so strong consistency is less critical. Use asynchronous replication with a replication lag SLA (e.g., < 1s).
