# Feature Store

## Problem Statement

Design a distributed feature store for ML systems that manages feature computation, online serving for low-latency inference, offline storage for training, and feature versioning with point-in-time correctness.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Feature registry**: Catalog all features with metadata (name, description, owner, type).
- **Online serving**: Low-latency feature retrieval for real-time inference (< 1ms).
- **Offline storage**: Historical feature data for model training in a data warehouse.
- **Feature computation**: Define features as transformations on raw data (SQL, Python).
- **Point-in-time correctness**: Retrieve feature values as of a specific timestamp for training.
- **Feature versioning**: Version features and track changes; support A/B testing.
- **Monitoring**: Track feature drift, staleness, and usage metrics.

### Non-Functional Requirements
- **Scale**: 10K+ features; 1M+ entities; 100K+ queries per second for online serving.
- **Latency**: Online feature retrieval < 1ms (p99); batch export < 1 hour for 1B rows.
- **Consistency**: Online and offline features must be computed identically (training-serving skew prevention).
- **Availability**: 99.99% uptime for online serving.

## Key Design Decisions
- **Dual storage**: Redis for online serving; data warehouse (BigQuery/Snowflake) for offline training.
- **Feature engineering as code**: Define features in Python/SQL; version-controlled and tested.
- **Stream processing**: Flink for real-time feature computation from Kafka events.
- **Point-in-time joins**: Time-travel queries in offline storage for correct training data.

## Architecture Overview

```
Raw Data → Kafka → Flink (Feature Computation)
                    → Online Store (Redis) → Inference Service
                    → Offline Store (Data Warehouse) → Training Pipeline
Feature Registry → Feature Definitions (Git) → CI/CD → Deploy
```

## Staff-Level Design Considerations

### Dual Storage Architecture
- **Online store**: Redis/Memcached for < 1ms feature retrieval. Store only the latest feature values.
- **Offline store**: BigQuery/Snowflake for historical features. Store all feature values with timestamps.
- **Staff insight**: The dual storage pattern is the defining characteristic of a feature store. Online serving needs speed (Redis); training needs history (data warehouse). The key challenge is keeping both stores consistent — use the same computation logic for both.

### Point-in-Time Correctness
- **Problem**: When training a model, you need feature values as of the prediction time, not the current time.
- **Solution**: Store all feature values with timestamps; use time-travel queries (e.g., BigQuery TIME_TRAVEL) to retrieve historical values.
- **Staff insight**: Point-in-time correctness is the #1 reason feature stores exist. Without it, training data leaks future information into the model (data leakage), producing overly optimistic metrics that fail in production. Always test point-in-time joins with known datasets.

### Feature Computation
- **Batch features**: Compute from historical data using SQL/spark; export to offline store periodically.
- **Stream features**: Compute in real-time using Flink from Kafka events; write to online store.
- **Staff insight**: Define features as code (Python/SQL) with unit tests. This ensures that the same feature computed in batch (for training) and in stream (for serving) produces identical results. Use a shared library for feature definitions.

### Training-Serving Skew Prevention
- **Problem**: Features computed differently in training vs serving leads to model degradation.
- **Solution**: Use the same feature computation code for both paths; test with the same input data.
- **Staff insight**: Training-serving skew is the #1 cause of model performance degradation in production. A feature store eliminates this by providing a single source of truth for feature computation. Always validate that online and offline features match for a sample of entities.

### Feature Monitoring
- **Drift detection**: Compare feature distributions between training data and production data.
- **Staleness**: Track the age of the latest feature value; alert if features are stale.
- **Staff insight**: Feature drift (distribution shift) is the leading cause of model degradation over time. Monitor feature distributions daily and alert on significant shifts. Use tools like Evidently or WhyLabs for automated drift detection.
