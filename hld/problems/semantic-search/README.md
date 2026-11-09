# Semantic Search Engine

## Problem Statement

Design a semantic search engine that understands query intent, retrieves relevant results using vector embeddings, and combines them with traditional keyword search for hybrid search with ranking, filtering, and autocomplete.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Semantic understanding**: Convert queries and documents into embeddings for meaning-based retrieval.
- **Hybrid search**: Combine vector similarity with keyword (BM25) search results.
- **Ranking**: Re-rank combined results using a learning-to-rank (LTR) model.
- **Filtering**: Support faceted search with filters (category, date, author, etc.).
- **Autocomplete**: Suggest queries in real-time as the user types.
- **Query understanding**: Handle synonyms, misspellings, and query rewriting.
- **Personalization**: Boost results based on user profile and search history.

### Non-Functional Requirements
- **Scale**: 1B+ documents; 100K+ queries per second.
- **Latency**: Search response < 200ms (p95); autocomplete < 50ms.
- **Relevance**: NDCG@10 > 0.8 on benchmark datasets.
- **Availability**: 99.9% uptime with graceful degradation to keyword-only search.

## Key Design Decisions
- **Embedding model**: Use a pre-trained bi-encoder (e.g., BERT-based) for fast encoding.
- **Vector index**: HNSW (Hierarchical Navigable Small World) for approximate nearest neighbor search.
- **Hybrid fusion**: Reciprocal Rank Fusion (RRF) to combine vector and BM25 scores.
- **Re-ranking**: Cross-encoder model (e.g., Cohere Rerank) for top-50 results.

## Architecture Overview

```
User Query → Query Parser → Embedding Service
                    → Vector DB (HNSW ANN) → Top-50 Results
                    → Keyword Index (BM25) → Top-50 Results
                    → Rank Fusion (RRF) → Re-ranker (Cross-encoder)
                    → Personalization → Final Results
Autocomplete → Prefix Tree → Suggestion Service
```

## Staff-Level Design Considerations

### Embedding Strategy
- **Bi-encoder**: Fast encoding (~1ms/document); independent encoding of query and document. Good for ANN search.
- **Tri-encoder**: Adds a re-ranking step for better accuracy at the cost of speed.
- **Staff insight**: Use a bi-encoder for the retrieval stage (fast) and a cross-encoder for re-ranking (accurate). This two-stage approach gives you the best of both worlds: speed at retrieval, accuracy at ranking.

### HNSW Index
- **Algorithm**: HNSW builds a layered graph for O(log n) nearest neighbor search.
- **Parameters**: M (max connections) and efConstruction control index quality vs build time.
- **Staff insight**: HNSW is the de facto standard for ANN search. Tune M=16 and efConstruction=200 for a good balance of recall and build time. Use efSearch=100 at query time for > 95% recall.

### Hybrid Search with RRF
- **Reciprocal Rank Fusion**: Score = Σ(1/(k + rank_i)) where k=60. No training needed.
- **Why hybrid**: Vector search captures semantics; BM25 captures exact keywords. Together they cover more ground.
- **Staff insight**: RRF is the simplest and most effective fusion method. It outperforms weighted score fusion in most cases because it doesn't require calibrating the relative scales of vector and BM25 scores.

### Re-Ranking
- **Cross-encoder**: Takes query + document pair as input; produces a relevance score. More accurate but slower (~50ms/pair).
- **Top-k selection**: Only re-rank top-50 fused results; return top-10.
- **Staff insight**: Re-ranking is the single biggest relevance improvement. It adds ~200ms for 50 documents but boosts NDCG@10 by 20-30%. Use a lightweight cross-encoder (e.g., MiniLM) for speed.

### Query Understanding
- **Spell correction**: Use a Levenshtein distance-based corrector or a language model.
- **Synonym expansion**: Maintain a synonym dictionary (e.g., "laptop" → "notebook computer").
- **Query rewriting**: Use an LLM to rewrite ambiguous queries for better retrieval.
- **Staff insight**: Query understanding is often overlooked but critical. 15-20% of searches have typos or ambiguous phrasing. Invest in spell correction and synonym expansion before considering LLM-based rewriting.
