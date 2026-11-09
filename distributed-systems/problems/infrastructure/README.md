# Infrastructure Services

Platform-level distributed services that provide foundational capabilities like unique ID generation, full-text search, and object storage at scale.

## Problems (3)

| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| [Distributed ID Generator](distributed-id-generator/) | Generate unique, ordered IDs without a central coordinator | Snowflake, UUID v7, batch pre-allocation, clock handling |
| [Distributed Search](distributed-search/) | Full-text search at scale like Elasticsearch/Algolia | Inverted index, sharding, relevance tuning, autocomplete |
| [Distributed File Storage](distributed-file-storage/) | Object storage at petabyte scale like Amazon S3 | Erasure coding, multipart upload, lifecycle, CDN |

## When to Use

- **Distributed ID Generator**: When your system needs unique primary keys that are time-sortable and don't require a central database (e.g., order IDs, transaction IDs, event sequence numbers).
- **Distributed Search**: When you need full-text search, faceting, filtering, or autocomplete across millions of documents (e.g., product search, log search, document indexing).
- **Distributed File Storage**: When you need to store unstructured data like images, videos, backups, or user uploads at petabyte scale (e.g., photo sharing, video streaming, data lake).

## Cross-References

- **Topics**: [Consistent Hashing](../coordination/consistent-hashing/) for data distribution across storage nodes
- **Related**: [Distributed Metrics](../observability/distributed-metrics/) stores time-series data similarly to file storage. [Distributed Search](distributed-search/) often indexes data stored in file storage systems.
