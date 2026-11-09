# E-commerce System - API Design

## API Overview

RESTful API with JSON responses. All endpoints require authentication via Bearer token except product browsing and search. Rate limited per user tier.

## Products & Catalog

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products (paginated, filterable) |
| GET | `/api/v1/products/{product_id}` | Get product details |
| GET | `/api/v1/products/{product_id}/reviews` | List product reviews |
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/{category_id}/products` | List products in category |

## Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/search?q={query}` | Search products |
| GET | `/api/v1/search/suggestions?q={query}` | Autocomplete suggestions |
| GET | `/api/v1/search/facets` | Get search facets (categories, brands, prices) |

## Cart

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cart` | Get current cart |
| POST | `/api/v1/cart/items` | Add item to cart |
| PUT | `/api/v1/cart/items/{item_id}` | Update item quantity |
| DELETE | `/api/v1/cart/items/{item_id}` | Remove item from cart |
| DELETE | `/api/v1/cart` | Clear cart |
| POST | `/api/v1/cart/merge` | Merge guest cart with authenticated cart |

## Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders` | Create order (checkout) |
| GET | `/api/v1/orders` | List user's orders (paginated) |
| GET | `/api/v1/orders/{order_id}` | Get order details |
| POST | `/api/v1/orders/{order_id}/cancel` | Cancel order |
| POST | `/api/v1/orders/{order_id}/return` | Initiate return |
| GET | `/api/v1/orders/{order_id}/tracking` | Get shipping tracking |

## Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/charge` | Process payment (idempotent) |
| POST | `/api/v1/payments/refund` | Refund payment |
| GET | `/api/v1/payments/{payment_id}` | Get payment status |
| GET | `/api/v1/payment-methods` | List user's payment methods |
| POST | `/api/v1/payment-methods` | Add payment method |
| DELETE | `/api/v1/payment-methods/{id}` | Remove payment method |

## Reviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/products/{product_id}/reviews` | Add review |
| GET | `/api/v1/products/{product_id}/reviews` | List reviews |
| PUT | `/api/v1/reviews/{review_id}` | Update review |
| DELETE | `/api/v1/reviews/{review_id}` | Delete review |

## Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get user profile |
| PUT | `/api/v1/users/me` | Update user profile |
| GET | `/api/v1/users/me/addresses` | List addresses |
| POST | `/api/v1/users/me/addresses` | Add address |
| PUT | `/api/v1/users/me/addresses/{id}` | Update address |
| DELETE | `/api/v1/users/me/addresses/{id}` | Remove address |
| GET | `/api/v1/users/me/wishlist` | Get wishlist |
| POST | `/api/v1/users/me/wishlist` | Add to wishlist |

## Staff-Level API Design Considerations

### Checkout Request
```json
{
  "order_id": "uuid-v4",
  "items": [{"product_id": "p123", "quantity": 2, "price": 29.99}],
  "shipping_address_id": "addr-456",
  "shipping_method": "standard",
  "payment_method_id": "pm-789",
  "idempotency_key": "uuid-v4"
}
```

### Pagination
- **Cursor-based** for product listings and orders
- **Offset-based** for admin operations
- Return `next_cursor`, `has_more`, `total_count`

### Idempotency
- All payment and order operations require `Idempotency-Key` header
- Same key returns original result without re-processing
- Key TTL: 24 hours
