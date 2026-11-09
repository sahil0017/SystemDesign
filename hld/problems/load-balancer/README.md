# Load Balancer

## Problem Statement

Design a load balancer that handles large-scale production workloads.

**Reference**: algomaster, algomaster, hellointerview, designgurus, educative, system-design-primer, awesome-system-design

## Requirements

### Functional Requirements
- **Real-Time Bidding**: Support real-time bidding with proper error handling.
- **Auction Engine**: Support auction engine with proper error handling.
- **Budget Pacing**: Support budget pacing with proper error handling.
- **Impression Tracking**: Support impression tracking with proper error handling.

### Non-Functional Requirements
- **Scale**: Handle 1M+ users
- **Latency**: P99 < 200ms
- **Availability**: 99.9% uptime
- **Consistency**: Eventual with configurable strong consistency

## Key Design Decisions
- **Architecture**: Microservices with API gateway
- **Data storage**: SQL vs NoSQL based on access patterns
- **Caching**: Multi-tier strategy
- **Key concepts**: Real-time bidding, Auction engine, Budget pacing, Impression tracking

## Architecture Overview

```
Publisher → Ad Server → Auction Engine
                        → Bidder Pool
                        → Creative Store
                        → Analytics Pipeline
```

## Staff-Level Design Considerations

### Scalability
- **Horizontal scaling**: Add instances behind load balancer
- **Staff insight**: Start simple; shard only when needed.

### Caching
- **Multi-tier**: CDN + Redis + app cache
- **Staff insight**: Use TTL jitter and single-flight to prevent stampede.

### Error Handling
- **Circuit breaker**: Prevent cascading failures
- **Staff insight**: Design for failure at every layer.

### Key Concepts: Real-time bidding, Auction engine, Budget pacing, Impression tracking
