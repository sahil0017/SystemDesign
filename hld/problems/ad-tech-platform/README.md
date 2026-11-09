# Ad Tech Platform (Google Ads-like)

## Problem Statement

Design an advertising technology platform that handles real-time ad auctions, targeted ad delivery, budget pacing, impression tracking, and fraud detection for a large-scale content platform with billions of ad impressions daily.

**Reference**: ByteByteGo, HelloInterview, DesignGurus

## Requirements

### Functional Requirements
- **Ad auction**: Real-time second-price auction (RTB) for ad slots with < 100ms latency.
- **Targeting**: Deliver ads based on user demographics, interests, location, and context.
- **Budget pacing**: Control advertiser spend rates to avoid early budget exhaustion.
- **Impression tracking**: Track ad impressions, clicks, and conversions with attribution.
- **Ad creative management**: Store and serve multiple ad formats (display, video, native).
- **Fraud detection**: Detect and filter invalid traffic (IVT) from bots and click farms.
- **Reporting**: Real-time dashboards for advertisers with spend, impressions, and ROI metrics.

### Non-Functional Requirements
- **Scale**: 10B+ ad impressions per day; 100K+ auctions per second.
- **Latency**: Ad auction and delivery < 100ms end-to-end.
- **Accuracy**: Budget pacing within 1% of daily target; attribution accuracy > 95%.
- **Availability**: 99.99% uptime; ad failures should fallback to default content.

## Key Design Decisions
- **Second-price auction**: Highest bidder wins but pays the second-highest bid + $0.01.
- **Real-time bidding (RTB)**: OpenRTB protocol for external demand sources.
- **Budget pacing**: Token bucket algorithm per campaign; smooth spend across the day.
- **Event tracking**: Kafka-based event pipeline for impressions, clicks, and conversions.

## Architecture Overview

```
Page Load → Ad Request → Ad Server
                    → Targeting Engine (User + Context)
                    → Auction Engine (RTB)
                    → Budget Pacer
                    → Creative Server → Ad Render
                    → Kafka → Event Processor → Reporting DB
```

## Staff-Level Design Considerations

### Real-Time Auction
- **Second-price auction**: Incentivizes truthful bidding; winner pays second-highest bid + epsilon.
- **RTB flow**: Ad request → bid requests to demand sources (50ms timeout) → select winner → return ad.
- **Staff insight**: The auction is the core revenue engine. Optimize for latency: parallel bid requests with 50ms timeout, local cache for targeting data, and pre-computed bid prices.

### Targeting Engine
- **User signals**: Demographics, interests, browsing history, past conversions.
- **Context signals**: Page category, content keywords, time of day, device type.
- **Data structures**: Bloom filters for interest matching; inverted indexes for audience segments.
- **Staff insight**: Targeting data is read-heavy. Cache all targeting data in Redis/Memcached with < 1ms lookup. Use bloom filters to quickly exclude non-matching audiences before expensive lookups.

### Budget Pacing
- **Token bucket**: Each campaign gets tokens proportional to its daily budget; each impression consumes tokens.
- **Time-based smoothing**: Adjust token refill rate based on time of day and historical spend patterns.
- **Staff insight**: Budget pacing prevents the "front-loading" problem where 80% of the budget is spent in the first 4 hours. Use a predictive pacing algorithm that adjusts bid multipliers based on remaining budget and remaining impressions.

### Event Tracking Pipeline
- **Impression events**: Fired when an ad is rendered; track ad ID, user ID, timestamp, price.
- **Click events**: Fired on ad click; attribute to the correct campaign with view-through window.
- **Conversion events**: Tracked via pixel/SDK; attributed to the last click or view within a window.
- **Staff insight**: The event pipeline is the source of truth for revenue reporting. Use Kafka for durability and Flink for real-time aggregation. Store raw events in a data lake (S3) for audit and reprocessing.

### Ad Fraud Detection
- **IVT detection**: Identify invalid traffic from bots, click farms, and emulators.
- **Signals**: IP reputation, device fingerprint, click velocity, geographic anomalies.
- **Real-time blocking**: Drop suspicious requests before the auction to save budget.
- **Staff insight**: Ad fraud costs the industry $30B+ annually. Use a combination of real-time rules (block known bad IPs) and ML models (detect anomalous patterns). Third-party verification (3P) from companies like DoubleVerify is standard.
