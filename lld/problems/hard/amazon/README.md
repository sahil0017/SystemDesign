# Amazon (E-commerce Marketplace)

## Problem Statement

Design an e-commerce marketplace like Amazon that supports product catalog, shopping cart, order management, payment processing, reviews, recommendations, and seller management.

**Reference**: AlgoMaster, LLD Coding

## Requirements

### Functional Requirements
- **Product catalog**: Browse, search, and filter products by category, price, brand, rating.
- **Shopping cart**: Add/remove items; update quantities; save for later.
- **Order management**: Place orders, track status, cancel/return items.
- **Payment**: Multiple payment methods; split payment; coupon/discount support.
- **Reviews/Ratings**: Write reviews, rate products, report abuse.
- **Seller management**: Third-party sellers can list products and manage inventory.
- **Recommendations**: "Customers who bought this also bought," personalized suggestions.

### Non-Functional Requirements
- **Scale**: 100M+ products; 500M+ users; 1M+ orders per day.
- **Latency**: Product search < 500ms; checkout < 3s.
- **Availability**: 99.99% uptime; graceful degradation during Black Friday.

## Key Design Decisions
- **Microservices**: Separate services for catalog, cart, order, payment, and review.
- **Search**: Elasticsearch for product search with faceted filtering.
- **Inventory**: Distributed inventory management with reservation on add-to-cart.
- **CQRS**: Command side for orders; query side for product browsing with denormalized data.

## Class Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────►│    Order     │────►│  OrderItem   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ - userId     │     │ - orderId    │     │ - productId  │
│ - name       │     │ - status     │     │ - quantity   │
│ - addresses  │     │ - totalPrice │     │ - price      │
└──────────────┘     │ - paymentId  │     └──────────────┘
                     └──────────────┘
                          │
                     ┌────┴────┐
                     │  Cart   │────►│  Product   │
                     ├─────────┤     ├────────────┤
                     │ - items │     │ - productId│
                     └─────────┘     │ - title    │
                                     │ - price    │
                                     │ - inventory│
                                     └────────────┘
```

## Staff-Level Design Considerations

### Inventory Management
- **Reservation model**: Reserve inventory on add-to-cart (30-minute TTL). Deduct on payment.
- **Staff insight**: During flash sales, use a token bucket to limit concurrent checkouts. Without it, overselling is inevitable.

### Search vs Catalog
- **Elasticsearch**: Full-text search with faceting. Sync from catalog DB via CDC (Change Data Capture).
- **Staff insight**: Never search the primary database directly. Use a search index that's eventually consistent with the source of truth.

### Recommendation Engine
- **Collaborative filtering**: Matrix factorization for "users who bought X also bought Y."
- **Staff insight**: Pre-compute recommendations offline (batch) and cache them. Real-time recommendations are too slow for the happy path.
