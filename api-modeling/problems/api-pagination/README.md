# API Pagination

## Problem Statement

Design pagination strategies for REST APIs including offset-based, cursor-based (keyset), and page-based pagination with performance considerations.

**Reference**: Educative.io, ByteByteGo

## Strategies

| Strategy | Query | Pros | Cons |
|----------|-------|------|------|
| Offset | `?offset=0&limit=20` | Simple | Slow with large offsets |
| Cursor | `?cursor=abc&limit=20` | Fast, consistent | Can't jump to page N |
| Page | `?page=2&size=20` | User-friendly | Same issues as offset |

## Staff-Level Insight

> "Cursor pagination for APIs, page pagination for admin UIs."

- **Staff insight**: Use **cursor-based pagination** for production APIs — `WHERE id > :cursor ORDER BY id LIMIT 20` is always O(1) regardless of position. Use **page-based** only for admin UIs where users need to jump to specific pages. Never expose `totalCount` for large collections — it requires a full COUNT query. Return `hasMore: true/false` instead.
