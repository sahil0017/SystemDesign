# Recommendation Engine

## Problem Statement

Design a recommendation engine that suggests relevant items (products, videos, articles) to users based on their behavior, preferences, and similar users' activity. The system must handle real-time recommendations at scale with personalized results.

**Reference**: Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **User profiling**: Track user behavior (views, clicks, purchases, ratings).
- **Item catalog**: Maintain metadata for all recommendable items.
- **Recommendation strategies**: Collaborative filtering, content-based, hybrid approaches.
- **Real-time updates**: Incorporate recent user actions into recommendations immediately.
- **Batch processing**: Periodic model training on historical data.
- **A/B testing**: Compare recommendation algorithms and strategies.
- **Diversity**: Avoid filter bubbles; include diverse recommendations.

### Non-Functional Requirements
- **Scale**: 100M+ users; 10M+ items; 1B+ interactions per day.
- **Latency**: Recommendation generation < 100ms for real-time requests.
- **Freshness**: Recommendations reflect user activity within 1 minute.
- **Accuracy**: High precision and recall; measured by CTR and conversion rate.

## Key Design Decisions
- **Two-phase approach**: Candidate generation (wide recall) → Ranking (precise scoring).
- **Feature store**: Centralized storage of user and item features for ML models.
- **Model serving**: Pre-computed recommendations cached; real-time re-ranking.
- **Event streaming**: Kafka for real-time user behavior events.

## Architecture Diagram

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Client  │───►│  API Gateway │───►│  Rec Service │───►│  Model       │
│          │    │              │    │              │    │  Serving     │
└──────────┘    └──────────────┘    └──────┬───────┘    └──────────────┘
                                            │
                                     ┌──────┴───────┐
                                     │  Feature     │
                                     │  Store       │
                                     └──────┬───────┘
                                            │
                              ┌─────────────┼─────────────┐
                              │             │             │
                       ┌──────┴──┐  ┌──────┴────┐ ┌─────┴──────┐
                       │ Kafka   │  │  Batch    │ │  Candidate  │
                       │ (Events)│  │  Training │ │  Generation │
                       └─────────┘  └───────────┘ └────────────┘
```

## Staff-Level Design Considerations

### Two-Phase Recommendation
- **Candidate generation**: Retrieve 100-1000 candidates from millions of items using fast heuristics.
- **Ranking**: Score and rank candidates using complex ML models.
- **Staff insight**: Never score all items with the ML model — it's too slow. Use a two-phase approach: fast recall (candidate generation) followed by precise scoring (ranking). This is the industry standard.

### Real-Time vs Batch
- **Real-time**: Use user's last N actions for immediate personalization.
- **Batch**: Train models periodically on historical data for long-term patterns.
- **Staff insight**: Combine both. Batch models capture long-term preferences. Real-time features capture immediate intent. Use a feature store to serve both types of features to the ranking model.

### Cold Start Problem
- **New users**: Recommend popular/trending items until enough behavior is collected.
- **New items**: Use content-based features (metadata, tags) until enough interactions exist.
- **Staff insight**: The cold start problem is unsolvable — you can't recommend what you don't know. Use exploration-exploitation (multi-armed bandit) to gradually learn user preferences while still providing relevant recommendations.

### Cache Strategy
- **Pre-computed recommendations**: Cache top-N recommendations per user; update periodically.
- **Staff insight**: Don't generate recommendations from scratch on every request. Pre-compute and cache the top-N for each user. Use real-time re-ranking to adjust based on recent activity. This reduces latency from seconds to milliseconds.
