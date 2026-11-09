# REST API Design Fundamentals

## Core Principles

REST (Representational State Transfer) is an architectural style for designing networked applications. It relies on a stateless, client-server, cacheable communications protocol — HTTP in almost all cases.

## Resource Naming

### Use Nouns, Not Verbs
```
✅ GET    /users/123          # Get user 123
✅ POST   /users              # Create a new user
✅ PUT    /users/123          # Update user 123
✅ DELETE /users/123          # Delete user 123
❌ GET    /getUser? id=123    # Imperative — not RESTful
❌ POST   /createUser         # Verb in URL
```

### Naming Conventions
- **Plural nouns** for collections: `/users`, `/orders`, `/products`
- **Nested resources** for relationships: `/users/123/orders`
- **Lowercase with hyphens**: `/order-items`, `/payment-methods`
- **Avoid file extensions**: `/users` not `/users.json`

## HTTP Methods

| Method | Action | Idempotent | Safe | Cacheable |
|--------|--------|-----------|------|-----------|
| GET | Read resource | Yes | Yes | Yes |
| POST | Create resource | No | No | No |
| PUT | Replace resource | Yes | No | No |
| PATCH | Partial update | No | No | No |
| DELETE | Remove resource | Yes | No | No |

## Status Codes

### Success (2xx)
- `200 OK` — General success
- `201 Created` — Resource created (POST)
- `204 No Content` — Success with no body (DELETE)

### Client Error (4xx)
- `400 Bad Request` — Invalid input
- `401 Unauthorized` — Authentication required
- `403 Forbidden` — Insufficient permissions
- `404 Not Found` — Resource doesn't exist
- `409 Conflict` — Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` — Validation error
- `429 Too Many Requests` — Rate limit exceeded

### Server Error (5xx)
- `500 Internal Server Error` — Unexpected error
- `502 Bad Gateway` — Upstream service error
- `503 Service Unavailable` — Service down
- `504 Gateway Timeout` — Upstream timeout

## HATEOAS (Hypermedia As The Engine Of Application State)

HATEOAS allows clients to discover available actions through links in responses:

```json
{
  "id": 123,
  "name": "John Doe",
  "status": "pending",
  "_links": {
    "self": { "href": "/users/123" },
    "orders": { "href": "/users/123/orders" },
    "update": { "href": "/users/123", "method": "PUT" },
    "delete": { "href": "/users/123", "method": "DELETE" }
  }
}
```

## Pagination

### Offset Pagination
```
GET /users?offset=0&limit=20
```
Response includes `total`, `offset`, `limit`, and `next_offset`.

### Cursor Pagination (Recommended)
```
GET /users?cursor=eyJpZCI6MTIzfQ&limit=20
```
Response includes `next_cursor` for the next page. More efficient for large datasets.

## Filtering, Sorting, and Searching

```
GET /users?status=active&role=admin&sort=-created_at&search=john
GET /products?price_gte=10&price_lte=100&category=electronics
```

## Staff-Level Insights

### API Design First
- Design APIs using **OpenAPI/Swagger** before implementation
- Review API contracts in PRs alongside code changes
- Use **contract testing** to ensure backend and frontend stay in sync

### Versioning Strategy
- Use **URI versioning** (`/v1/users`) for major breaking changes
- Use **header versioning** for client-specific versions
- Never break backward compatibility within a version

### Response Consistency
- Always wrap responses in a consistent envelope
- Include metadata (pagination, timestamps) in every response
- Use consistent error format across all endpoints
