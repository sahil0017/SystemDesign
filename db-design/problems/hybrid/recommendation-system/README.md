# Recommendation System Hybrid Database Architecture

## Problem Statement

Design a hybrid database architecture for a recommendation system that processes user behavior data, generates recommendations, and serves them with low latency. Use PostgreSQL for user profiles, Cassandra for behavior events, Redis for cached recommendations, and an ML pipeline for batch and real-time personalization. Implement two-phase recommendations (candidate generation + ranking) and a feature store.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **User Profiles**: Demographics, preferences, purchase history from PostgreSQL.
- **Behavior Events**: Clicks, views, adds-to-cart, purchases stored in Cassandra.
- **Candidate Generation**: Broad filtering to produce 100-1000 candidate items.
- **Ranking**: ML model scores and ranks candidates to top-N (10-50).
- **Real-Time Features**: Update recommendations on user action (click, purchase).
- **A/B Testing**: Serve different recommendation models to user segments.
- **Cold Start**: Handle new users and new items without history.

### Non-Functional Requirements
- **Latency**: < 200ms for full recommendation pipeline (p99).
- **Throughput**: 100K recommendation requests/second.
- **Freshness**: Recommendations update within 1 minute of user action.
- **Scalability**: 100M users, 10M items.
- **Model versioning**: Track and rollback ML model versions.

## Key Design Decisions

- **Two-phase architecture**: Candidate generation (fast filter) → ranking (ML score).
- **Pre-computed recommendations**: Batch job pre-computes top-N per user; stored in Redis.
- **Real-time feature updates**: User actions stream to feature store for live personalization.
- **Feature store**: Centralized storage of ML features for training and serving.
- **A/B testing via Redis**: Different recommendation lists keyed by experiment group.

## Architecture

```
┌─────────────┐    ┌──────────┐    ┌───────────┐
│  PostgreSQL │    │ Cassandra│    │   Redis   │
│ (User Profs)│    │(Behavior)│    │(Rec Cache)│
└──────┬──────┘    └──────┬───┘    └─────┬─────┘
       │                  │              │
       ▼                  ▼              ▼
┌─────────────────────────────────────────────────┐
│              ML Pipeline                        │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Batch Training│  │ Real-Time Feature Store│  │
│  │ (Daily)       │  │ (Kafka + Redis)        │  │
│  └──────────────┘  └────────────────────────┘  │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ Rec Server     │
              │ 1. Candidate   │  ← Redis (pre-computed)
              │ 2. Ranking     │  ← Feature Store (real-time)
              │ 3. Re-ranking  │  ← Business rules
              └────────────────┘
```

## Schema Design

### PostgreSQL (User Profiles)

```sql
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY,
    age_range VARCHAR(10),
    gender VARCHAR(10),
    country VARCHAR(100),
    city VARCHAR(100),
    language VARCHAR(10),
    registered_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP,
    preferences JSONB, -- {"categories": ["electronics", "books"], "brands": ["Nike"]}
    lifetime_value DECIMAL(12,2) DEFAULT 0,
    total_purchases INT DEFAULT 0
);

CREATE TABLE user_purchase_history (
    purchase_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    product_id UUID NOT NULL,
    category_id BIGINT,
    amount DECIMAL(10,2),
    purchased_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

CREATE INDEX idx_purchase_user ON user_purchase_history(user_id, purchased_at DESC);
CREATE INDEX idx_purchase_category ON user_purchase_history(category_id, purchased_at DESC);
```

### Cassandra (Behavior Events)

```cql
-- User behavior events for feature extraction
CREATE TABLE user_behavior (
    user_id TEXT,
    event_date TEXT,
    timestamp TIMESTAMP,
    event_type TEXT, -- 'view', 'click', 'add_to_cart', 'purchase', 'search'
    product_id TEXT,
    category_id TEXT,
    session_id TEXT,
    properties MAP<TEXT, TEXT>,
    PRIMARY KEY ((user_id, event_date), timestamp, event_type)
) WITH CLUSTERING ORDER BY (timestamp ASC)
  AND default_time_to_live = 2592000; -- 30 days

-- Product interaction counts (for popularity-based candidate gen)
CREATE TABLE product_interactions (
    product_id TEXT,
    event_date TEXT,
    event_type TEXT,
    view_count COUNTER,
    click_count COUNTER,
    purchase_count COUNTER,
    PRIMARY KEY ((product_id, event_date), event_type)
);
```

### Redis (Cached Recommendations)

```
# Pre-computed recommendations per user
Key:    rec:{user_id}:for_you
Type:   List
Value:  [product_id_1, product_id_2, ..., product_id_50]
TTL:    30 minutes

# Real-time feature: recent user interactions
Key:    feature:{user_id}:recent_views
Type:   Sorted Set
Value:  {product_id: timestamp_score}
TTL:    1 hour

# Product embeddings for similarity search
Key:    embedding:{product_id}
Type:   String (binary vector)
Value:  [0.12, -0.45, 0.78, ...]  (128-dim float vector)
TTL:    No TTL

# A/B test assignment
Key:    experiment:{user_id}:rec_model
Type:   String
Value:  "v2_collaborative_filtering"
TTL:    30 days

# Popularity scores (for candidate generation)
Key:    popularity:daily:{date}
Type:   Sorted Set
Value:  {product_id: purchase_count}
TTL:    7 days
```

### Feature Store Schema

```
# Online feature store (Redis - low latency serving)
Key:    fs:{user_id}:{feature_name}
Type:   String/Hash
TTL:    1 hour

Features:
  - fs:{user_id}:avg_order_value → "45.50"
  - fs:{user_id}:favorite_categories → '{"electronics":0.6,"books":0.3}'
  - fs:{user_id}:recency_score → "0.85"
  - fs:{user_id}:frequency_score → "0.72"

# Offline feature store (Parquet on S3 - training)
s3://feature-store/
├── user_features/
│   ├── date=2024-01-15/
│   │   └── part-00000.parquet
├── item_features/
│   ├── date=2024-01-15/
│   │   └── part-00000.parquet
└── interaction_features/
    ├── date=2024-01-15/
    │   └── part-00000.parquet
```

### ML Model Registry

```sql
CREATE TABLE model_versions (
    model_id UUID PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version INT NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'collaborative_filtering', 'content_based', 'hybrid'
    metrics JSONB, -- {"precision@10": 0.45, "recall@10": 0.32, "ndcg@10": 0.38}
    training_data_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'training', -- 'training', 'validated', 'deployed', 'archived'
    s3_path TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (model_name, version)
);

CREATE TABLE ab_experiments (
    experiment_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model_id UUID NOT NULL,
    traffic_percentage DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',
    start_date DATE NOT NULL,
    end_date DATE,
    metrics JSONB,
    FOREIGN KEY (model_id) REFERENCES model_versions(model_id)
);
```

## Recommendation Pipeline

### Two-Phase Recommendation Flow

```
Phase 1: Candidate Generation (50ms)
├─ Popularity-based: Top 100 trending items (Redis sorted set)
├─ Collaborative filtering: Users similar to you liked... (pre-computed)
├─ Content-based: Similar to items you viewed (embedding similarity)
└─ Merge & deduplicate → 500 candidates

Phase 2: Ranking (100ms)
├─ Fetch features: User features + item features (Feature Store)
├─ ML model scoring: XGBoost/Neural Net scores each candidate
├─ Re-ranking: Business rules (diversity, freshness, inventory)
└─ Return top-50 → Cache in Redis (30 min TTL)
```

### Real-Time Update Flow

```
User clicks product → 
  1. Write behavior event to Cassandra
  2. Publish to Kafka: user_behavior topic
  3. Feature store consumer updates Redis features
  4. Invalidate Redis rec cache for user
  5. Next request triggers fresh recommendation
```

## Staff-Level Design Considerations

### Pre-Computation vs Real-Time
- **Pre-compute top-N**: Batch job runs every hour; stores in Redis.
- **Staff insight**: Don't run the full ML pipeline on every request — it's too slow. Pre-compute recommendations for active users and cache in Redis. Use real-time features only for re-ranking the top candidates, not for full candidate generation. This reduces p99 latency from 2s to 200ms.

### Cold Start Problem
- **New users**: Show trending/popular items until enough behavior data.
- **New items**: Boost in content-based recommendations; use item attributes for similarity.
- **Staff insight**: Hybrid approach: blend popularity (50%), content-based (30%), and collaborative filtering (20%) for new users. As behavior data accumulates, increase CF weight. For new items, use a "new item boost" that decays over 7 days to give them exposure.

### Feature Store Pattern
- **Online store**: Redis for low-latency feature serving (< 5ms).
- **Offline store**: S3 + Parquet for batch model training.
- **Staff insight**: The key challenge is training-serving skew — features used during training must match features used during serving. A feature store (e.g., Feast, Tecton) ensures the same feature computation code runs for both. Point-in-time correct queries prevent data leakage during training.

### A/B Testing Infrastructure
- **User hashing**: `hash(user_id) % 100` determines experiment group.
- **Staff insight**: Use consistent hashing for experiment assignment so the same user always sees the same variant. Store the assignment in Redis to avoid recomputation. Track metrics (CTR, conversion rate, revenue per user) per experiment. Run experiments for at least 2 weeks to account for day-of-week effects.

### Embedding Similarity Search
- **Cosine similarity**: Find similar items by comparing embedding vectors.
- **Staff insight**: For 10M items, brute-force similarity search is O(N) — too slow. Use approximate nearest neighbor (ANN) search with FAISS or HNSW index. Redis 7+ supports vector similarity search via `FT.SEARCH` with vector fields. This reduces similarity search from 100ms to < 5ms with 95%+ recall.
