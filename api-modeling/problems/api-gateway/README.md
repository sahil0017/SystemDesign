# API Gateway

## Problem Statement

Design an API Gateway that handles routing, authentication, rate limiting, request aggregation, circuit breaking, and monitoring for a microservices architecture.

**Reference**: Educative.io, ByteByteGo

## Key Responsibilities

- **Routing**: Forward requests to appropriate backend services
- **Authentication**: Validate JWT/API keys before forwarding
- **Rate limiting**: Per-client and per-endpoint rate limits
- **Aggregation**: Combine multiple service responses into one
- **Circuit breaking**: Protect backend services from overload
- **Monitoring**: Track latency, error rates, and throughput

## Architecture

```
Client --> API Gateway --> Service A
                  |-- Service B
                  |-- Service C
                  |
                  +-- Auth Service
                  +-- Rate Limiter (Redis)
                  +-- Circuit Breaker
```

## Staff-Level Insight

> "API Gateway is the single entry point for all client requests."

- **Staff insight**: Use **Kong**, **APISIX**, or **AWS API Gateway** for production. Implement **request aggregation** at the gateway to reduce client round trips. Use **circuit breaker** per backend service — if Service A is down, return cached/fallback data instead of timing out. Track **latency per route** to identify slow services.
