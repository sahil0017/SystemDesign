# Lazy vs Eager Loading

## Trade-off Overview

Lazy loading fetches data only when needed. Eager loading fetches all related data upfront. The choice affects initial response time, memory usage, and the N+1 query problem.

## Lazy Loading
- **Pros**: Loads only needed data, lower initial memory, flexible.
- **Cons**: N+1 query problem, slower overall if all data is needed.
- **Use when**: Large entities with optional related data, uncertain access patterns.

## Eager Loading
- **Pros**: Fewer queries (JOIN or batch load), predictable performance.
- **Cons**: Loads unused data, higher initial memory, complex queries.
- **Use when**: All related data is needed, performance-critical paths.

## Staff-Level Insight

> "Eager load what you know you need. Lazy load what you might need."

- **Staff insight**: Use **eager loading** for known access patterns (e.g., order page always shows order items). Use **lazy loading** for optional data (e.g., order audit log). In ORMs, use **JOIN FETCH** (Hibernate) or **Include** (Entity Framework) for eager loading. Profile N+1 queries with SQL logging — they are the #1 performance anti-pattern in ORM-based applications.
