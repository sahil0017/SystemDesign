# Product Catalog NoSQL Schema Design

## Problem Statement

Design a NoSQL schema for a high-read product catalog (like Amazon) with products, categories, attributes, pricing, inventory, and reviews. Optimize for read-heavy workloads with denormalization, caching, and efficient attribute-based filtering.

**Reference**: AlgoMaster, Educative.io, ByteByteGo

## Requirements

### Functional Requirements
- **Products**: Name, description, price, images, brand, category, attributes.
- **Categories**: Hierarchical browsing (Electronics → Phones → Smartphones).
- **Attributes**: Size, color, material, weight — varies by product type.
- **Pricing**: Current price, sale price, currency, price history.
- **Inventory**: Stock quantity, warehouse locations, availability status.
- **Reviews**: Rating, title, body, verified purchase, helpful votes.
- **Search**: Filter by category, brand, price range, attributes.

### Non-Functional Requirements
- **Read throughput**: 100K reads/second for product detail pages.
- **Filter performance**: Attribute-based filtering in < 100ms.
- **Denormalization**: Minimize joins for product detail page.
- **Cache-friendly**: Hot products served from cache.
- **Consistency**: Eventually consistent reads acceptable for catalog.

## Key Design Decisions

- **Denormalized product document**: Category, brand, and attributes embedded in product.
- **Read-replica caching**: Redis cache for hot products with cache-aside pattern.
- **Attribute filtering**: DynamoDB Global Secondary Indexes (GSI) for filter queries.
- **Review aggregation**: Pre-computed average rating and count on product document.
- **Price updates**: Versioned price history for audit and rollback.

## Schema Design (DynamoDB)

### Products Table (Main)

```json
{
  "TableName": "Products",
  "KeySchema": [
    { "AttributeName": "product_id", "KeyType": "HASH" },
    { "AttributeName": "sort_key", "KeyType": "RANGE" }
  ],
  "AttributeDefinitions": [
    { "AttributeName": "product_id", "AttributeType": "S" },
    { "AttributeName": "sort_key", "AttributeType": "S" },
    { "AttributeName": "category_id", "AttributeType": "S" },
    { "AttributeName": "brand", "AttributeType": "S" },
    { "AttributeName": "price", "AttributeType": "N" },
    { "AttributeName": "status", "AttributeType": "S" }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "CategoryIndex",
      "KeySchema": [
        { "AttributeName": "category_id", "KeyType": "HASH" },
        { "AttributeName": "sort_key", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    },
    {
      "IndexName": "BrandIndex",
      "KeySchema": [
        { "AttributeName": "brand", "KeyType": "HASH" },
        { "AttributeName": "sort_key", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    },
    {
      "IndexName": "PriceRangeIndex",
      "KeySchema": [
        { "AttributeName": "status", "KeyType": "HASH" },
        { "AttributeName": "price", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    }
  ]
}
```

### Product Item Structure

```json
{
  "product_id": "P-12345",
  "sort_key": "PRODUCT#P-12345",
  "name": "Nike Air Max 270",
  "description": "Comfortable running shoe with Air Max cushioning...",
  "category_id": "CAT-SHOES-RUNNING",
  "category_path": "/Footwear/Shoes/Running",
  "brand": "Nike",
  "price": 150.00,
  "sale_price": 120.00,
  "currency": "USD",
  "images": ["https://cdn.example.com/nike-air-max-270-1.jpg"],
  "attributes": {
    "size": ["US 8", "US 9", "US 10", "US 11"],
    "color": ["Black", "White", "Red"],
    "material": "Mesh",
    "weight_grams": 250
  },
  "stock_quantity": 500,
  "is_available": true,
  "average_rating": 4.5,
  "review_count": 1250,
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-20T15:30:00Z"
}
```

### Reviews Table

```json
{
  "TableName": "Reviews",
  "KeySchema": [
    { "AttributeName": "product_id", "KeyType": "HASH" },
    { "AttributeName": "review_id", "KeyType": "RANGE" }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "UserReviewIndex",
      "KeySchema": [
        { "AttributeName": "user_id", "KeyType": "HASH" },
        { "AttributeName": "created_at", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    },
    {
      "IndexName": "RatingIndex",
      "KeySchema": [
        { "AttributeName": "product_id", "KeyType": "HASH" },
        { "AttributeName": "rating", "KeyType": "RANGE" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    }
  ]
}
```

### Price History Table

```json
{
  "TableName": "PriceHistory",
  "KeySchema": [
    { "AttributeName": "product_id", "KeyType": "HASH" },
    { "AttributeName": "changed_at", "KeyType": "RANGE" }
  ]
}
```

### Redis Cache Keys

| Key Pattern | Type | Purpose | TTL |
|------------|------|---------|-----|
| `product:{product_id}` | Hash | Full product document | 1 hour |
| `product:price:{product_id}` | String | Price only (hot path) | 5 min |
| `product:stock:{product_id}` | String | Stock quantity | 1 min |
| `category:{category_id}:products` | Set | Product IDs in category | 30 min |
| `brand:{brand}:products` | Set | Product IDs by brand | 30 min |
| `search:{query_hash}` | String | Search result cache | 5 min |

## Indexes Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| `Products` | PK: `product_id`, SK: `sort_key` | Product detail lookup |
| `Products` | GSI: `CategoryIndex` | Browse by category |
| `Products` | GSI: `BrandIndex` | Browse by brand |
| `Products` | GSI: `PriceRangeIndex` | Price range filtering |
| `Reviews` | PK: `product_id`, SK: `review_id` | Product's reviews |
| `Reviews` | GSI: `UserReviewIndex` | User's review history |
| `Reviews` | GSI: `RatingIndex` | Filter reviews by rating |
| `PriceHistory` | PK: `product_id`, SK: `changed_at` | Price change audit |

## Staff-Level Design Considerations

### Denormalization Strategy
- **Embedded category**: Store `category_path` in product document to avoid join.
- **Staff insight**: In NoSQL, reads are expensive (multiple round trips). Denormalize freely — store `category_name`, `brand_name`, and even `review_summary` in the product document. Update these via background job or event-driven sync when source data changes. Storage is cheap; latency is expensive.

### Review Rating Aggregation
- **Pre-computed average**: `average_rating` and `review_count` stored on product document.
- **Staff insight**: Never calculate average rating at read time — it requires scanning all reviews. Update the aggregate on each new review write. Use a running average formula: `new_avg = (old_avg * old_count + new_rating) / (old_count + 1)`. This is O(1) update vs O(N) scan.

### Attribute Filtering
- **DynamoDB GSI**: Global Secondary Indexes enable filtering by category, brand, and price.
- **Staff insight**: DynamoDB GSI has a 1 RCU/base read cost and eventual consistency by default. For complex multi-attribute filtering (e.g., "shoes + Nike + size 10 + under $200"), use Elasticsearch as the primary search engine and DynamoDB as the source of truth. Sync via DynamoDB Streams → Elasticsearch.

### Cache Invalidation
- **Cache-aside pattern**: App checks cache first; on miss, reads from DynamoDB and populates cache.
- **Staff insight**: Product updates are infrequent compared to reads. Use write-through invalidation: on product update, delete the cache key (`DEL product:{id}`). Don't update the cache directly — let the next read populate it with fresh data. This avoids stale cache during rapid updates.

### Price Update Versioning
- **Price history**: Every price change creates a new row in `PriceHistory` table.
- **Staff insight**: Price changes affect orders, refunds, and analytics. Store the full history with `changed_at`, `old_price`, `new_price`, and `changed_by`. This enables price rollback, audit trails, and "price at purchase time" for order history.
