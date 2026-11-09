# E-commerce Database Schema Design

## Problem Statement

Design a comprehensive database schema for an e-commerce platform that supports product catalog management, orders, payments, inventory tracking, user management, reviews, and promotions. The schema must handle high write throughput during sales events and support complex analytical queries.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Product Catalog**: Categories, products, variants (size, color), pricing, images, attributes.
- **User Management**: Users, addresses, wishlists, order history.
- **Shopping Cart**: Persistent cart, guest cart, coupon application.
- **Orders**: Order lifecycle (pending → confirmed → shipped → delivered/returned), order items, shipping.
- **Payments**: Multiple payment methods, refunds, idempotency.
- **Inventory**: Stock tracking, reserved stock, reorder thresholds, warehouse locations.
- **Reviews & Ratings**: Product reviews, verified purchase flag, helpful votes.
- **Promotions**: Coupons, flash sales, bundle deals, loyalty points.

### Non-Functional Requirements
- **ACID compliance**: Orders and payments must be transactionally consistent.
- **Read scalability**: Product catalog reads >> writes; support caching layer.
- **Write scalability**: Handle 10K orders/second during flash sales.
- **Data integrity**: Prevent overselling, ensure payment idempotency.
- **Analytics support**: Historical queries on orders, revenue, user behavior.

## Key Design Decisions

- **Normalization vs Denormalization**: Normalize orders/payments for integrity; denormalize product catalog for read performance.
- **Partitioning**: Partition orders table by `created_at` for time-based queries and archival.
- **Soft deletes**: Use `is_active` flags instead of physical deletes for audit trail.
- **JSONB for flexibility**: Store product attributes and shipping tracking data as JSONB.
- **Optimistic locking**: Use `version` column on inventory to prevent concurrent stock updates.

## Schema Design

### Core Tables

```sql
-- Users & Addresses
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
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
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Product Catalog
CREATE TABLE categories (
    category_id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id BIGINT,
    sort_order INT DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES categories(category_id)
);

CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    category_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    attributes JSONB, -- {"brand": "Nike", "material": "Cotton"}
    images TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE product_variants (
    variant_id UUID PRIMARY KEY,
    product_id UUID NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    options JSONB NOT NULL, -- {"size": "M", "color": "Red"}
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    version INT NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Orders
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending_payment',
    subtotal DECIMAL(12,2) NOT NULL,
    tax DECIMAL(12,2) NOT NULL,
    shipping_cost DECIMAL(12,2) NOT NULL,
    discount DECIMAL(12,2) DEFAULT 0,
    total DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address_id BIGINT,
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
);

CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    variant_id UUID NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    variant_options JSONB,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Payments
CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    method VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    provider_transaction_id VARCHAR(100),
    idempotency_key VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Reviews
CREATE TABLE reviews (
    review_id BIGINT PRIMARY KEY,
    product_id UUID NOT NULL,
    user_id BIGINT NOT NULL,
    order_item_id BIGINT,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    body TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Promotions
CREATE TABLE coupons (
    coupon_id BIGINT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'percentage', 'fixed', 'free_shipping'
    value DECIMAL(10,2),
    min_order_amount DECIMAL(10,2) DEFAULT 0,
    max_discount DECIMAL(10,2),
    usage_limit INT,
    usage_count INT DEFAULT 0,
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `orders` | `(user_id, created_at DESC)` | User order history |
| `orders` | `(status, created_at DESC)` | Admin order management |
| `orders` | Partition by `created_at` | Time-based queries, archival |
| `products` | GIN on `attributes` | JSONB attribute search |
| `product_variants` | Unique on `sku` | SKU lookup |
| `payments` | Unique on `idempotency_key` | Payment deduplication |
| `reviews` | `(product_id, created_at DESC)` | Product reviews listing |
| `addresses` | `(user_id, is_default)` | Default address lookup |

## Staff-Level Design Considerations

### Preventing Overselling
- **Optimistic locking**: `version` column on `product_variants`; retry on conflict.
- **Reserved stock**: Separate `reserved_quantity` to hold inventory during checkout.
- **Staff insight**: Use `SELECT ... FOR UPDATE` on inventory row during checkout to prevent race conditions. Combine with Redis Lua script for atomic check-and-decrement.

### Order Partitioning
- **Range partitioning**: Partition `orders` by month for efficient time-range queries.
- **Staff insight**: Old orders move to cold storage automatically. Active partitions stay on fast SSD; archived partitions on cheaper storage.

### Payment Idempotency
- **Unique constraint**: `idempotency_key` prevents duplicate payment processing.
- **Staff insight**: Client generates UUID per payment attempt. On retry, server returns cached result instead of reprocessing. This is critical for distributed systems where network retries are common.

### Product Catalog Read Optimization
- **Denormalization**: Store `product_name` and `variant_options` in `order_items` for historical record.
- **Staff insight**: Never join product tables for order history queries — product data changes over time. Denormalize at order time for accurate historical records.

### Analytics Queries
- **Materialized views**: Pre-aggregate daily revenue, top products, user cohorts.
- **Staff insight**: Don't run analytical queries on operational tables. Use materialized views refreshed hourly or a separate data warehouse (e.g., Snowflake, BigQuery) via CDC.
