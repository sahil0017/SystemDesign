# Logging

## Problem Statement (Staff-Level)

Design and implement a logging with proper OOP principles.

**Reference**: algomaster, designgurus, educative

## Requirements

### Functional Requirements
- **Design Patterns**: Support design patterns with proper error handling.
- **Oop**: Support oop with proper error handling.
- **Solid Principles**: Support solid principles with proper error handling.

### Non-Functional Requirements
- **Scale**: Handle 1M+ users
- **Latency**: P99 < 200ms
- **Availability**: 99.9% uptime
- **Consistency**: Eventual with configurable strong consistency

## Key Design Decisions
- **Architecture**: Microservices with API gateway
- **Data storage**: SQL vs NoSQL based on access patterns
- **Caching**: Multi-tier strategy
- **Key concepts**: Design patterns, OOP, SOLID principles

## Class Diagram

```
┌──────────────┐     ┌──────────────┐
│   Logging   │────►│   Manager    │
├──────────────┤     ├──────────────┤
│ - properties │     │ - items      │
└──────────────┘     └──────────────┘
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

### Key Concepts: Design patterns, OOP, SOLID principles
