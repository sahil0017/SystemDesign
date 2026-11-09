# Fraud Detection System

## Problem Statement

Design a real-time fraud detection system that analyzes transactions, user behavior, and device fingerprints to identify fraudulent activity using rule-based engines, ML models, and stream processing with sub-100ms latency.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Real-time scoring**: Score each transaction for fraud risk in < 100ms.
- **Rule engine**: Configurable rules (e.g., "flag if amount > $10K and new device").
- **ML model serving**: Run pre-trained fraud models (XGBoost, neural nets) on transaction features.
- **Feature store**: Compute and serve real-time features (e.g., "transactions in last hour").
- **Behavioral analysis**: Track user session patterns, velocity checks, and anomaly detection.
- **Device fingerprinting**: Identify and track devices across sessions.
- **Case management**: Queue flagged transactions for manual review with investigation tools.
- **Feedback loop**: Use investigator decisions to retrain models.

### Non-Functional Requirements
- **Scale**: 1M+ transactions per second; 10B+ events per day.
- **Latency**: End-to-end fraud decision < 100ms (p99).
- **Accuracy**: False positive rate < 1%; false negative rate < 0.1%.
- **Availability**: 99.99% uptime; fraud checks must not block transactions on failure.

## Key Design Decisions
- **Stream processing**: Use Kafka + Flink for real-time feature computation and event processing.
- **Feature store**: Redis for low-latency feature serving; offline store for training data.
- **Two-stage scoring**: Fast rule engine first; ML model only for borderline cases.
- **Async review**: Flagged transactions go to a queue for manual review without blocking.

## Architecture Overview

```
Transaction → API Gateway → Fraud Detection Service
                                    → Rule Engine (fast path)
                                    → Feature Store (Redis)
                                    → ML Scoring Service (model server)
                                    → Decision Engine → Allow/Flag/Block
                                    → Kafka → Stream Processor (Flink)
                                    → Case Management → Investigator UI
```

## Staff-Level Design Considerations

### Two-Stage Scoring
- **Stage 1 (Rules)**: Sub-10ms decision using configurable rules. Clear obvious legitimate and obvious fraudulent transactions.
- **Stage 2 (ML)**: Only score borderline transactions with ML models. Adds 50-80ms but catches complex patterns.
- **Staff insight**: This pattern reduces ML model load by 60-80% since most transactions are clearly legitimate or clearly fraudulent. It's the key to meeting latency SLAs.

### Feature Store Design
- **Online features**: Stored in Redis for < 1ms access (e.g., "transaction count in last hour").
- **Offline features**: Stored in data warehouse for model training (historical aggregates).
- **Feature computation**: Flink jobs compute features in real-time from Kafka events.
- **Staff insight**: Feature consistency between training and serving is the #1 challenge. Use a unified feature store (e.g., Feast) to ensure the same features are used in both paths.

### Rule Engine
- **Drools/JSON rules**: Configurable without code changes; hot-reload on update.
- **Rule prioritization**: Order rules by selectivity; most specific rules first.
- **Staff insight**: Rules are the first line of defense. They're interpretable, fast, and easy to update. Keep a small set of high-impact rules and let ML handle the rest.

### Stream Processing with Flink
- **Event-time processing**: Use event timestamps, not processing time, for accurate windowing.
- **State management**: Flink state backend (RocksDB) for maintaining user session state.
- **Watermarks**: Handle late-arriving events with configurable watermark intervals.
- **Staff insight**: Flink is the best choice for fraud detection because of its exactly-once semantics and low-latency windowing. Use tumbling windows for velocity checks and session windows for behavioral analysis.

### Feedback Loop
- **Investigator decisions**: When an investigator confirms or rejects a fraud case, log the decision.
- **Model retraining**: Use confirmed cases as labeled data for weekly model retraining.
- **Staff insight**: The feedback loop is what makes the system improve over time. Without it, the model degrades as fraud patterns evolve. Automate retraining with a CI/CD pipeline for ML models.
