# GraphQL vs REST

## Trade-off Overview

GraphQL lets clients request exactly the data they need. REST exposes fixed endpoints with fixed response shapes. The choice affects over-fetching, caching, and API evolution.

## REST
- **Pros**: Simple caching (HTTP cache), predictable performance, mature tooling.
- **Cons**: Over-fetching/under-fetching, multiple round trips, fixed endpoints.
- **Use when**: Simple APIs, caching is critical, team familiarity.

## GraphQL
- **Pros**: Client specifies fields, single endpoint, strong typing, introspection.
- **Cons**: Complex caching, N+1 queries, query complexity attacks.
- **Use when**: Multiple clients (web, mobile, IoT), evolving data needs.

## Staff-Level Insight

> "REST for simplicity and caching. GraphQL when clients have diverse data needs."

- **Staff insight**: Use **REST for backend services** where caching and simplicity matter. Use **GraphQL as a BFF (Backend for Frontend)** layer — it aggregates multiple REST/gRPC calls into one response for the client. Don't expose GraphQL directly to the public — use it as an aggregation layer. Implement **query depth limiting** and **cost analysis** to prevent abuse. Use **DataLoader** to solve N+1 queries in GraphQL resolvers.
