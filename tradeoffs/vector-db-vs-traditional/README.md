# Vector DB vs Traditional DB

## Trade-off: When to Use Vector Databases vs Traditional Databases

### Context

With the rise of AI/ML applications, vector databases have emerged as a new storage paradigm. Understanding when to use vector DBs vs traditional databases (SQL/NoSQL) is critical for system design decisions.

### Vector Database

**Best for**: Semantic search, similarity matching, recommendation systems, anomaly detection.

**Strengths**:
- **ANN search**: Optimized for approximate nearest neighbor search with HNSW/IVF-PQ indexes.
- **Semantic understanding**: Find similar items by meaning, not exact matches.
- **ML-native**: Store and query embeddings directly; no need for external services.
- **Hybrid search**: Combine vector similarity with metadata filtering.

**Weaknesses**:
- **No transactions**: Most vector DBs don't support ACID transactions.
- **Limited querying**: No complex joins, aggregations, or subqueries.
- **Cost**: High memory usage for HNSW indexes (2-3x vector size).
- **Maturity**: Younger ecosystem; fewer tooling and integrations.

### Traditional Database

**Best for**: Structured data, transactions, complex queries, reporting, and operational workloads.

**Strengths**:
- **ACID transactions**: Strong consistency for financial and operational data.
- **Rich querying**: Complex joins, aggregations, subqueries, and window functions.
- **Maturity**: Decades of tooling, monitoring, and operational knowledge.
- **Cost**: Well-optimized storage; cheaper per GB for structured data.

**Weaknesses**:
- **No semantic search**: Can only do exact match or keyword search (full-text).
- **Limited similarity**: No native support for vector similarity search.
- **Scaling**: Harder to scale for unstructured data workloads.

### Decision Framework

| Criteria | Choose Vector DB | Choose Traditional DB |
|----------|-----------------|----------------------|
| Primary query type | Similarity search | Exact match, joins, aggregations |
| Data type | Embeddings, unstructured | Structured, relational |
| Consistency needs | Eventual consistency | Strong consistency (ACID) |
| Scale | 100M+ vectors | < 100M rows with complex queries |
| Query latency | < 100ms ANN search | < 10ms point lookup |

### Staff Insight

**Use both**. In most production systems, you need both a vector DB (for semantic search) and a traditional DB (for metadata and transactions). The vector DB stores embeddings and handles similarity search, while the traditional DB stores user data, transactions, and business logic. Use change data capture (CDC) to keep them in sync.

**pgvector exception**: If your vector workload is < 10M vectors and you already use PostgreSQL, pgvector gives you vector search in your existing database. It's a good compromise for small-to-medium workloads.

### Real-World Examples

- **Netflix**: Uses vector DB (Milvus) for content recommendations + PostgreSQL for user data and transactions.
- **Pinterest**: Uses vector DB for visual search + Cassandra for pin metadata and user feeds.
- **Spotify**: Uses vector DB for music recommendations + PostgreSQL for user accounts and playlists.
