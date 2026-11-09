# API Versioning

## Problem Statement

Design an API versioning strategy that supports backward compatibility, graceful deprecation, and smooth migration for clients.

**Reference**: Educative.io, ByteByteGo

## Strategies

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URI versioning | `/api/v1/users` | Simple, explicit, cacheable | Pollutes URI |
| Header versioning | `Accept: v1` | Clean URI | Harder to debug |
| Query parameter | `/api/users?version=1` | Easy to test | Not RESTful |
| Content negotiation | `Accept: application/vnd.api.v1+json` | Standards-based | Complex |

## Deprecation Strategy

1. **Launch v2**: Support both v1 and v2 simultaneously
2. **Notify**: Return `Deprecation: true` and `Sunset: 2025-06-01` headers on v1
3. **Document**: Publish migration guide from v1 to v2
4. **Monitor**: Track v1 usage; notify top consumers directly
5. **Shutdown**: Disable v1 after sunset date; return 410 Gone

## Staff-Level Insight

> "Version when you make breaking changes. Never break existing clients."

- **Breaking changes**: Renaming fields, changing types, removing endpoints, changing validation rules.
- **Non-breaking**: Adding fields, adding endpoints, relaxing validation.
- **Staff insight**: Use **URI versioning** (`/api/v1/`) — it's explicit and cacheable. Support old versions for **at least 1 year**. Use **feature flags** instead of versioning when possible — add new field in v1 with default value, enable gradually. Version only when you must break backward compatibility.
