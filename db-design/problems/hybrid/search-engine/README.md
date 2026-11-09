# Search Engine Hybrid Database Architecture

## Problem Statement

Design a hybrid database architecture for a search engine that indexes content from relational databases and serves full-text search queries. Use PostgreSQL as the source of truth and Elasticsearch for search indexing. Handle index synchronization, search relevance tuning, faceted search, and autocomplete.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Source Data**: Products, articles, users stored in PostgreSQL.
- **Search Index**: Full-text search with relevance scoring in Elasticsearch.
- **Index Sync**: Near-real-time synchronization from PostgreSQL to Elasticsearch.
- **Faceted Search**: Filter by category, brand, price range, attributes.
- **Autocomplete**: Type-ahead suggestions as user types.
- **Search Analytics**: Track queries, click-through rate, zero-result queries.

### Non-Functional Requirements
- **Search latency**: < 100ms for 95% of queries.
- **Index freshness**: Changes visible in search within 1 minute.
- **Scalability**: 10M+ documents, 10K queries/second.
- **Relevance**: Tunable ranking with business rules (boost popular items).
- **Fault tolerance**: Search remains available during index rebuild.

## Key Design Decisions

- **PostgreSQL as source of truth**: All CRUD operations go to PostgreSQL first.
- **Elasticsearch for search**: Full-text, faceting, autocomplete, relevance tuning.
- **CDC for sync**: Debezium captures changes → Kafka → Elasticsearch indexer.
- **Search analytics**: Track query performance and user behavior.
- **Rolling index rebuild**: Zero-downtime index migration.

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌───────────────┐
│  PostgreSQL │────►│ Debezium │────►│  Kafka   │────►│  ES Indexer   │
│  (Source)   │     │ (CDC)    │     │ (Stream) │     │  (Consumer)   │
└─────────────┘     └──────────┘     └──────────┘     └───────┬───────┘
                                                               │
┌─────────────┐                                               ▼
│  API Server │──────────────────────────────────────────┐  ┌───────────────┐
│  (Search)   │  HTTP Query                              │  │  Elasticsearch │
└─────────────┘                                          └─►│  (Search)     │
     │                                                      └───────────────┘
     ▼
┌─────────────┐
│  Dashboard  │  ← Search analytics (queries, CTR, zero-results)
└─────────────┘
```

## Schema Design

### PostgreSQL (Source of Truth)

```sql
-- Products table (same as e-commerce schema)
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    category_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    brand VARCHAR(100),
    attributes JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    popularity_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Elasticsearch Index Mapping

```json
PUT /products
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "product_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "synonym_filter"]
        }
      },
      "filter": {
        "synonym_filter": {
          "type": "synonym",
          "synonyms_path": "synonyms.txt"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "product_id": { "type": "keyword" },
      "name": {
        "type": "text",
        "analyzer": "product_analyzer",
        "fields": {
          "keyword": { "type": "keyword" },
          "suggest": { "type": "completion" }
        }
      },
      "description": { "type": "text", "analyzer": "product_analyzer" },
      "category": { "type": "keyword" },
      "brand": { "type": "keyword" },
      "price": { "type": "float" },
      "currency": { "type": "keyword" },
      "attributes": {
        "type": "flattened"
      },
      "is_active": { "type": "boolean" },
      "popularity_score": { "type": "integer" },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" }
    }
  }
}
```

### Autocomplete Index

```json
PUT /product_suggestions
{
  "mappings": {
    "properties": {
      "suggestion": {
        "type": "completion",
        "payloads": true
      }
    }
  }
}

# Index a suggestion
POST /product_suggestions/_doc/1
{
  "suggestion": {
    "input": ["Nike Air Max", "Air Max 270", "Running Shoes"],
    "output": "Nike Air Max 270",
    "payload": {
      "product_id": "P-12345",
      "category": "Shoes"
    }
  }
}
```

### Search Analytics (PostgreSQL)

```sql
CREATE TABLE search_queries (
    query_id BIGINT PRIMARY KEY,
    search_query VARCHAR(500) NOT NULL,
    result_count INT NOT NULL,
    click_count INT DEFAULT 0,
    clicked_product_id UUID,
    response_time_ms INT,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_search_queries_time ON search_queries(created_at DESC);
CREATE INDEX idx_search_queries_text ON search_queries USING gin(to_tsvector('english', search_query));
```

### Kafka Topics

```
# CDC changes from PostgreSQL
Topic: db.products.changes
Partition key: product_id
Schema: Avro (Debezium)
Retention: 7 days

# Elasticsearch index commands
Topic: es.products.index
Partition key: product_id
Schema: JSON
Retention: 1 day
```

## Index Synchronization

### CDC-Based Sync Flow

```
1. Product created/updated in PostgreSQL
2. Debezium captures change from WAL
3. Event published to Kafka: db.products.changes
4. ES Indexer consumer reads event
5. Transform to Elasticsearch document format
6. Index/update in Elasticsearch via bulk API
7. Acknowledge Kafka offset
```

### ES Indexer Consumer (Pseudocode)

```python
def process_cdc_event(event):
    op = event.operation  # 'c', 'u', 'd'
    product_id = event.data.product_id
    
    if op == 'd':
        es.delete(index='products', id=product_id)
    else:
        doc = transform_to_es_doc(event.data)
        es.index(index='products', id=product_id, body=doc)
    
    # Also update autocomplete
    if op in ('c', 'u'):
        es.index(index='product_suggestions', id=product_id, body={
            'suggestion': {
                'input': [event.data.name, event.data.brand],
                'output': event.data.name,
                'payload': {'product_id': product_id}
            }
        })
```

## Staff-Level Design Considerations

### Near-Real-Time Index Sync
- **CDC via Debezium**: Changes reach Elasticsearch within seconds.
- **Staff insight**: Don't use polling (e.g., "updated_at > last_sync") — it misses rapid changes and adds OLTP load. CDC via WAL is zero-impact and captures every change. The end-to-end latency (WAL → Kafka → ES) is typically 1-5 seconds.

### Search Result Consistency
- **Eventual consistency**: Elasticsearch is eventually consistent with PostgreSQL.
- **Staff insight**: After creating/updating a product in PostgreSQL, the search index may lag by seconds. For "create then search" flows, read the product from PostgreSQL directly for the first few seconds. Use a write-through cache or redirect to detail page (not search results) after creation.

### Relevance Tuning
- **BM25 + function score**: Base relevance from BM25; boost by popularity, recency, business rules.
- **Staff insight**: Default BM25 ranking is rarely good enough. Use `function_score` query to boost: popular products (`popularity_score`), recently added items (recency decay), sponsored products (business rule), and items in stock. A/B test different boosting strategies and track CTR (click-through rate) as the primary metric.

### Rolling Index Rebuild
- **Alias-based swap**: Create new index, reindex, swap alias — zero downtime.
- **Staff insight**: When changing mappings (e.g., add new field), you can't update an existing index. Create `products-v2`, reindex from `products-v1`, then swap the alias: `POST /_aliases { "actions": [{ "add": { "index": "products-v2", "alias": "products" }}, { "remove": { "index": "products-v1", "alias": "products" }}] }`. The swap is atomic — queries see the new index instantly.

### Shard Count Planning
- **5 shards**: For 10M documents with 1GB/shard limit.
- **Staff insight**: You can't change shard count after index creation. Plan for growth: 1 shard = 10-50GB max. For 10M products at ~500 bytes each = ~5GB, so 5 shards with 1 replica provides headroom. Too many shards (< 1GB each) wastes memory on shard metadata. Too few shards (> 50GB) limits single-node capacity.
