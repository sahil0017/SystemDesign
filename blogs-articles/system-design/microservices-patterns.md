# Microservices Patterns

## Overview

Microservices decompose monolithic applications into independently deployable services. This article covers the essential patterns for building, communicating, and managing microservices at scale.

## Communication Patterns

### Synchronous (Request-Response)
- **REST/HTTP**: Simple, language-agnostic, good for external APIs
- **gRPC**: High-performance internal communication with Protobuf
- **Problem**: Tight coupling, cascading failures, latency accumulation

### Asynchronous (Event-Driven)
- **Message Queue** (RabbitMQ): Guaranteed delivery, routing flexibility
- **Event Streaming** (Kafka): High throughput, replay capability
- **Benefit**: Loose coupling, resilience, scalability

### Anti-Corruption Layer
- Isolate internal domain model from external service interfaces
- Use **API Gateway** pattern to translate between external and internal models
- Prevents external changes from propagating through the system

## Data Management Patterns

### Database per Service
- Each service owns its database — no shared schemas
- **Benefit**: Loose coupling, independent scaling, technology choice
- **Challenge**: Cross-service queries require API calls or CQRS

### Saga Pattern
For distributed transactions across services:
- **Choreography**: Each service publishes events; next service reacts
- **Orchestration**: Central coordinator directs the transaction flow
- **Compensation**: Each step has an undo operation for rollback

```
Order Service → Payment Service → Inventory Service
     ↓                ↓                  ↓
  Create Order    Charge Card        Reserve Items
     ↓                ↓                  ↓
 (if fail)      Refund Card      Release Items (compensation)
```

### CQRS (Command Query Responsibility Segregation)
- Separate read and write models for independent scaling
- Commands update the write model; events update read models
- Read models are denormalized for fast queries

## Deployment Patterns

### API Gateway
- Single entry point for all client requests
- Handles: routing, authentication, rate limiting, request aggregation
- Examples: Kong, Apigee, AWS API Gateway

### Service Mesh
- Infrastructure layer for service-to-service communication
- Handles: load balancing, circuit breaking, observability, mTLS
- Examples: Istio, Linkerd

### Sidecar Pattern
- Deploy helper container alongside main service
- Handles: logging, monitoring, service discovery
- Used by service meshes for transparent traffic management

## Staff-Level Insights

### When NOT to Use Microservices
- **Small teams**: Monolith is faster to develop and deploy
- **Simple domain**: No need for distributed complexity
- **High transactional consistency**: ACID across services is hard
- **Staff insight**: Start with a **modular monolith**; split into microservices when you have clear scaling or team boundaries.

### Bounded Contexts
- Use **Domain-Driven Design** to identify service boundaries
- Each bounded context becomes a candidate service
- Avoid splitting by technical layer (no "user-service" and "user-db-service")

### Observability is Non-Negotiable
- Distributed tracing for request flow across services
- Centralized logging with correlation IDs
- Metrics for each service's health and performance
- **Staff insight**: Without observability, microservices become a debugging nightmare. Invest in the three pillars (metrics, logs, traces) from day one.
