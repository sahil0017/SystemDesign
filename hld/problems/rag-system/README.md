# RAG (Retrieval-Augmented Generation) System

## Problem Statement

Design a Retrieval-Augmented Generation (RAG) system that combines vector-based document retrieval with LLM generation, supporting semantic search, hybrid query strategies, real-time document updates, and multi-tenant isolation.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Document ingestion**: Parse and chunk documents (PDF, Markdown, HTML) into embeddings.
- **Vector storage**: Store and index embeddings in a vector database for similarity search.
- **Semantic search**: Retrieve top-k relevant chunks based on query embeddings.
- **Hybrid search**: Combine vector similarity with keyword (BM25) search for better recall.
- **LLM generation**: Feed retrieved context to an LLM for grounded, citation-rich responses.
- **Multi-tenancy**: Isolate documents and queries per tenant with RBAC.
- **Real-time updates**: Support document additions, updates, and deletions with index refresh.
- **Citations**: Return source document references with page/section links.

### Non-Functional Requirements
- **Scale**: 100M+ document chunks; 10K+ queries per second.
- **Latency**: End-to-end query < 2s (embedding < 100ms, retrieval < 200ms, LLM < 1.5s).
- **Accuracy**: Top-5 retrieval recall > 90% on benchmark datasets.
- **Availability**: 99.9% uptime with graceful degradation (fallback to keyword search).

## Key Design Decisions
- **Embedding model**: Use a pre-trained model (e.g., text-embedding-3-large) for consistent vector quality.
- **Vector database**: Choose between Pinecone, Weaviate, Milvus, or pgvector based on scale and cost.
- **Chunking strategy**: Fixed-size overlap chunks (512 tokens, 50-token overlap) for context preservation.
- **Hybrid search**: Fuse vector and BM25 scores with reciprocal rank fusion (RRF) for best recall.

## Architecture Overview

```
User Query → API Gateway → Embedding Service → Vector DB (ANN Search)
                                              → Keyword Index (BM25)
                                              → Rank Fusion → Context Builder
                                              → LLM Service → Response + Citations
Document Ingestion → Parser → Chunker → Embedding Service → Vector DB + Keyword Index
```

## Staff-Level Design Considerations

### Chunking Strategy
- **Fixed-size overlap**: Simple and effective; 512-token chunks with 50-token overlap preserve context across boundaries.
- **Semantic chunking**: Use NLP to split at sentence/paragraph boundaries for better coherence.
- **Staff insight**: Start with fixed-size overlap. If retrieval quality is poor, switch to semantic chunking with a parent-document retriever pattern.

### Vector Database Selection
- **Pinecone**: Fully managed, easy to use, but expensive at scale.
- **Weaviate/Milvus**: Open-source, self-hosted, better cost control.
- **pgvector**: Best if you already use PostgreSQL; good for < 10M vectors.
- **Staff insight**: For production RAG at scale, use a dedicated vector DB (Milvus/Weaviate) with HNSW indexing. Avoid pgvector for > 10M vectors due to query latency.

### Hybrid Search with RRF
- **Reciprocal Rank Fusion**: Combine vector and BM25 ranks without training. Score = Σ(1/(k + rank_i)) where k=60.
- **Staff insight**: Pure vector search misses exact keyword matches. Pure BM25 misses semantic similarity. RRF gives you the best of both with no tuning.

### Context Window Management
- **Token budgeting**: Limit retrieved context to 70% of LLM context window; leave room for system prompt and response.
- **Re-ranking**: Use a cross-encoder re-ranker (e.g., Cohere Rerank) on top-50 retrieved chunks to select top-5 for the LLM.
- **Staff insight**: The re-ranker is the single biggest quality improvement. It adds ~200ms latency but boosts answer accuracy by 20-30%.

### Multi-Tenancy
- **Metadata filtering**: Store tenant ID as metadata in vector DB; filter at query time.
- **Namespace isolation**: Separate collections/indexes per tenant for strict isolation.
- **Staff insight**: Metadata filtering is cheaper and simpler. Namespace isolation is only needed for compliance (e.g., HIPAA, GDPR).
