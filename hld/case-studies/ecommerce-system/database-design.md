# E-commerce System - Database Design

## Database Strategy

- **PostgreSQL**: Orders, payments, users, inventory (ACID transactions)
- **Cassandra**: Product catalog, reviews (high read throughput)
- **Redis**: Product cache, session cart, inventory counters, rate limiting
- **Elasticsearch**: Product search with faceting and autocomplete

## PostgreSQL Schema

### Users & Addresses
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE addresses (
    address_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_addresses_user ON addresses(user_id, is_default);
```

### Orders
```sql
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending_payment', 'confirmed', 'shipped', 'delivered', 'cancelled', 'returned'
    subtotal DECIMAL(12,2) NOT NULL,
    tax DECIMAL(12,2) NOT NULL,
    shipping_cost DECIMAL(12,2) NOT NULL,
    total DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address_id BIGINT,
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id UUID NOT NULL,
    product_name VARCHAR(255) NOT NULL, -- Denormalized for historical record
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_orders_user ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status, created_at DESC);
```

### Payments
```sql
CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50) NOT NULL, -- 'credit_card', 'paypal', 'wallet'
    status VARCHAR(20) NOT NULL, -- 'pending', 'completed', 'refunded', 'failed'
    provider_transaction_id VARCHAR(100),
    idempotency_key VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_payments_order ON payments(order_id);
```

### Inventory
```sql
CREATE TABLE inventory (
    product_id UUID PRIMARY KEY,
    stock_quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    reorder_threshold INT NOT NULL DEFAULT 10,
    version INT NOT NULL DEFAULT 0, -- Optimistic locking
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Available stock = stock_quantity - reserved_quantity
CREATE INDEX idx_inventory_low_stock ON inventory (stock_quantity - reserved_quantity) WHERE (stock_quantity - reserved_quantity) < reorder_threshold;
```

## Cassandra Schema (Product Catalog & Reviews)

### Products
```sql
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    currency TEXT DEFAULT 'USD',
    category_id BIGINT,
    brand TEXT,
    images LIST<TEXT>,
    attributes MAP<TEXT, TEXT>, -- size, color, material
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Product Reviews
```sql
CREATE TABLE product_reviews (
    product_id UUID,
    created_at TIMESTAMP,
    review_id UUID,
    user_id BIGINT,
    rating INT,
    title TEXT,
    body TEXT,
    is_verified_purchase BOOLEAN,
    PRIMARY KEY (product_id, created_at, review_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

## Redis Data Structures

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `product:{product_id}` | Hash | Product cache | 1h |
| `cart:{user_id}` | Hash | Shopping cart items | 30 days |
| `cart:{session_id}` | Hash | Guest cart | 7 days |
| `inventory:{product_id}` | String | Stock counter | No TTL |
| `inventory:reserved:{product_id}:{order_id}` | String | Reserved stock | 15min |
| `rate:{user_id}:{endpoint}` | String | Rate limit counter | 1min |
| `search:{query}` | String | Search result cache | 5min |

## Elasticsearch Schema

### Product Index
```json
{
  "mappings": {
    "properties": {
      "product_id": { "type": "keyword" },
      "name": { "type": "text", "analyzer": "standard" },
      "description": { "type": "text" },
      "category": { "type": "keyword" },
      "brand": { "type": "keyword" },
      "price": { "type": "float" },
      "attributes": { "type": "keyword" },
      "is_active": { "type": "boolean" },
      "created_at": { "type": "date" }
    }
  }
}
```

## Indexes Strategy

### PostgreSQL Indexes
- **Order lookup**: Composite index on `(user_id, created_at DESC)`
- **Order status**: Composite index on `(status, created_at DESC)` for admin queries
- **Inventory**: Partial index for low-stock alerts
- **Payment idempotency**: Unique index on `idempotency_key`

### Cassandra Partition Strategy
- **Products**: Partition by `product_id` for direct lookup
- **Reviews**: Partition by `product_id`, cluster by `created_at DESC`
- **Replication factor**: 3 for high availability

## Staff-Level Database Considerations

### Inventory Management
- **Optimistic locking**: Version column prevents concurrent stock updates
- **Reserved stock**: Separate counter for checkout-reserved inventory
- **Atomic decrement**: Lua script in Redis for stock check-and-decrement
- **Staff insight**: Use **database-level constraints** (`CHECK stock_quantity >= 0`) as safety net

### Order State Machine
- States: `pending_payment → confirmed → shipped → delivered` or `→ cancelled/returned`
- Use **database triggers** or **application-level validation** for state transitions
- **Audit trail**: Store state changes in separate table for compliance

### Payment Idempotency
- **Idempotency key**: Client-generated UUID per payment attempt
- **Unique constraint**: On `idempotency_key` column
- **Return cached result**: If key exists, return original payment result
