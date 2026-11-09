# REST API Design

## Problem Statement

Design a comprehensive REST API for an e-commerce platform that follows RESTful conventions, proper resource naming, HTTP methods, status codes, pagination, filtering, sorting, and HATEOAS principles.

**Reference**: Educative.io, ByteByteGo, HelloInterview

## Requirements

### Functional Requirements
- **Resource modeling**: Users, Products, Orders, Payments as REST resources.
- **HTTP methods**: GET (read), POST (create), PUT (update), PATCH (partial update), DELETE.
- **Status codes**: 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 404 (Not Found), 409 (Conflict), 422 (Unprocessable Entity).
- **Pagination**: Cursor-based pagination for large collections.
- **Filtering**: Query parameters for filtering (`?status=active&category=electronics`).
- **Sorting**: Query parameters for sorting (`?sort=-createdAt`).
- **HATEOAS**: Links in responses for related resources.

### Non-Functional Requirements
- **Idempotency**: PUT and DELETE are idempotent.
- **Cacheability**: Proper Cache-Control headers for GET responses.
- **Versioning**: API versioned via URI (`/api/v1/`).
- **Error handling**: RFC 7807 Problem Detail format for errors.

## API Design

### Resources

```
GET    /api/v1/users                    # List users (paginated)
POST   /api/v1/users                    # Create user
GET    /api/v1/users/{id}               # Get user
PUT    /api/v1/users/{id}               # Update user
PATCH  /api/v1/users/{id}               # Partial update user
DELETE /api/v1/users/{id}               # Delete user

GET    /api/v1/products                 # List products (filter, sort, paginate)
POST   /api/v1/products                 # Create product
GET    /api/v1/products/{id}            # Get product
PUT    /api/v1/products/{id}            # Update product
DELETE /api/v1/products/{id}            # Delete product

GET    /api/v1/orders                   # List orders for authenticated user
POST   /api/v1/orders                   # Create order
GET    /api/v1/orders/{id}              # Get order
PUT    /api/v1/orders/{id}/cancel       # Cancel order (action as sub-resource)
```

### Response Format

```json
// GET /api/v1/products?limit=10&cursor=abc123
{
  "data": [
    {
      "id": "prod_123",
      "name": "Laptop",
      "price": 999.99,
      "currency": "USD",
      "category": "electronics",
      "createdAt": "2024-01-01T00:00:00Z",
      "_links": {
        "self": { "href": "/api/v1/products/prod_123" },
        "reviews": { "href": "/api/v1/products/prod_123/reviews" }
      }
    }
  ],
  "pagination": {
    "next": "/api/v1/products?limit=10&cursor=def456",
    "prev": "/api/v1/products?limit=10&cursor=xyz789"
  },
  "meta": {
    "totalCount": 1500,
    "hasMore": true
  }
}
```

### Error Format (RFC 7807)

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "instance": "/api/v1/orders",
  "errors": [
    { "field": "email", "message": "Invalid email format" },
    { "field": "quantity", "message": "Must be greater than 0" }
  ]
}
```

## Staff-Level Design Considerations

### Resource Naming
- **Nouns, not verbs**: `/orders` not `/getOrders`. HTTP method is the verb.
- **Plural nouns**: `/users` not `/user`. Collections are plural.
- **Nested resources**: `/users/{id}/orders` for user's orders.
- **Staff insight**: Keep nesting to **2 levels max**. Deep nesting (`/a/b/c/d/e`) indicates poor design. Use query parameters instead: `/orders?userId=123`.

### HTTP Methods
- **GET**: Safe, idempotent, cacheable. No side effects.
- **POST**: Create resource. Not idempotent. Use for actions that don't fit CRUD.
- **PUT**: Replace entire resource. Idempotent. Client sends full representation.
- **PATCH**: Partial update. Not idempotent. Client sends changes only.
- **Staff insight**: Use **POST for actions** that don't map to CRUD: `POST /orders/{id}/cancel`, `POST /users/{id}/reset-password`. Don't use DELETE for actions with side effects — use POST.

### Pagination Strategy
- **Offset-based**: `?offset=0&limit=20` — simple but inconsistent with inserts/deletes.
- **Cursor-based**: `?cursor=abc123&limit=20` — consistent, performant with indexed columns.
- **Staff insight**: Use **cursor-based pagination** for production APIs. Offset pagination has performance issues with large offsets (`OFFSET 100000` scans 100K rows). Cursor pagination uses `WHERE id > :cursor LIMIT 20` — always fast. Return cursor in response for next page.

### API Versioning
- **URI versioning**: `/api/v1/users` — simple, explicit, cacheable.
- **Header versioning**: `Accept: application/vnd.api.v1+json` — clean URI, harder to debug.
- **Staff insight**: Use **URI versioning** — it's explicit, cacheable, and easy to debug. When deprecating v1, return `Deprecation: true` and `Sunset: 2025-01-01` headers. Support old versions for at least 1 year after new version launch.
