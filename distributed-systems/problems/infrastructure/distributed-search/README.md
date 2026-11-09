# Distributed Search System

## Problem Statement

Design a distributed full-text search system (like Elasticsearch or Algolia) that indexes documents from multiple sources, supports complex queries (full-text, faceting, filtering, autocomplete), and provides low-latency search results at scale. The system must handle index updates, relevance tuning, and high query throughput.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Indexing**: Ingest documents from multiple sources (DB, Kafka, APIs) with schema mapping.
- **Full-text search**: Tokenization, stemming, synonym support, fuzzy matching.
- **Filtering**: Filter by facets (category, price range, date range, tags).
- **Sorting**: Sort by relevance, date, price, or custom fields.
- **Autocomplete**: Prefix-based suggestions with typo tolerance.
- **Aggregations**: Count, avg, min, max, histogram on indexed fields.
- **Highlighting**: Highlight matching terms in search results.

### Non-Functional Requirements
- **Query latency**: P95 search response in < 200ms.
- **Indexing throughput**: Ingest 100K documents/second.
- **Scalability**: Index 10B+ documents across multiple clusters.
- **Availability**: Search available during index updates and node failures.

## Key Design Decisions
- **Inverted index**: Core data structure for fast term-to-document lookup.
- **Sharding**: Split index across multiple shards for horizontal scaling.
- **Replication**: Replica shards for high availability and read scaling.
- **Near-real-time**: Index refresh interval (1s) balances freshness vs performance.

## Architecture

```
Data Sources              Indexing Layer              Search Layer
   |                          |                          |
   +-- PostgreSQL ----+       |                          |
   +-- Kafka --------+--> Ingestion --> Index Writer --> Shards (Primary + Replica)
   +-- API ----------+       |                          |
                                    |                          |
                                    +--> Refresh (1s) -------->|
                                                              |
                                    Client Query <-------------+
                                                              |
                                    +--> Cache (Hot Queries) --+
```

## Staff-Level Design Considerations

### Inverted Index Design
- **Term dictionary**: Maps terms to posting lists (document IDs + positions).
- **Posting list**: Sorted list of document IDs containing the term, with frequency and position.
- **Staff insight**: Use **FST (Finite State Transducer)** for term dictionary — compresses millions of terms into memory-efficient structure. Elasticsearch uses FST for term dictionary, enabling fast prefix queries and low memory usage.

### Index Refresh Strategy
- **Real-time**: Every document write is immediately searchable — high overhead.
- **Near-real-time**: Refresh index every 1 second — balances freshness and performance.
- **Batch**: Refresh every N minutes — best performance, lowest freshness.
- **Staff insight**: Use **1-second refresh** for most use cases. If you need real-time search (e.g., live bidding), use a separate real-time index with higher refresh rate. For analytics, use 5-minute refresh. Adjust per index based on freshness requirements.

### Relevance Tuning
- **BM25 algorithm**: Default ranking function; considers term frequency, document frequency, field length.
- **Custom scoring**: Boost specific fields (title > description > tags).
- **Staff insight**: Start with **BM25 defaults** — they work well for most use cases. Tune only when users report poor results. Common tuning: boost title field 2x, boost recent documents with decay function, use synonym filters for domain-specific terms.

### Sharding Strategy
- **Number of shards**: Balance between parallelism and per-shard data size.
- **Shard size**: Keep shards under 50GB for efficient rebalancing.
- **Staff insight**: Calculate shards as `total_data_size / 50GB`. For 1TB of data, use 20 primary shards. Too many small shards waste memory (each shard opens Lucene segments). Too few large shards can't be rebalanced efficiently.

### Autocomplete Implementation
- **N-gram analyzer**: Index character n-grams for prefix and middle-of-word matching.
- **Completion suggester**: Dedicated data structure for fast prefix queries.
- **Staff insight**: Use **completion suggester** for strict prefix autocomplete (e.g., search bar). Use **n-gram analyzer** for fuzzy autocomplete (e.g., "appple" → "apple"). N-gram increases index size 5-10x; use only when fuzzy matching is needed.
