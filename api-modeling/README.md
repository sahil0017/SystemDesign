# API Modeling

Comprehensive module for designing, documenting, and testing APIs at staff-engineer level. Covers REST, gRPC, GraphQL, API versioning, security, pagination, error handling, and API gateway patterns.

**References**: [Educative.io](https://www.educative.io/), [ByteByteGo](https://bytebytego.com/), [HelloInterview](https://www.hellointerview.com/)

## Contents

### Fundamentals
- [REST API Design](fundamentals/rest-api-design.md) — Resource naming, HTTP methods, status codes, HATEOAS
- [API Versioning](fundamentals/api-versioning.md) — URI versioning, header versioning, content negotiation
- [API Security](fundamentals/api-security.md) — OAuth 2.0, JWT, API keys, rate limiting, CORS

### Practice Problems (10 Problems)

| Problem | Key Concepts |
|---------|-------------|
| [REST API Design](problems/rest-api-design/) | Resource modeling, HTTP methods, status codes, HATEOAS |
| [gRPC API Design](problems/grpc-api-design/) | Protobuf, streaming, code generation, interceptors |
| [GraphQL API Design](problems/graphql-api-design/) | Schema design, resolvers, DataLoader, subscriptions |
| [API Versioning](problems/api-versioning/) | URI vs header versioning, deprecation strategy, backward compatibility |
| [API Gateway](problems/api-gateway/) | Routing, aggregation, rate limiting, authentication, circuit breaking |
| [Webhook Design](problems/webhook-design/) | Event delivery, retry logic, signature verification, idempotency |
| [OpenAPI Specification](problems/openapi-spec/) | Contract-first design, code generation, documentation |
| [API Security](problems/api-security/) | OAuth 2.0, JWT, API keys, CORS, CSRF protection |
| [API Pagination](problems/api-pagination/) | Offset, cursor, keyset pagination, performance |
| [API Error Handling](problems/api-error-handling/) | Error codes, retryable errors, problem detail RFC 7807 |

### Tests
- [API Design Tests](tests/) — Comprehensive test cases for API design patterns

## How to Use

1. **Start with fundamentals**: Read REST API design, versioning, and security guides
2. **Practice problems**: Implement each API design problem with proper patterns
3. **Run tests**: Validate your API designs against the test suite
4. **Review patterns**: Study API gateway, webhook, and OpenAPI patterns
