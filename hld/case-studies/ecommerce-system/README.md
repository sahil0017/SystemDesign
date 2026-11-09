# E-commerce System

## Problem Statement

Design an e-commerce platform like Amazon that supports product catalog management, shopping cart, order processing, payment integration, inventory management, shipping, reviews, and recommendations at scale (10M+ products, 100K+ orders/day).

## Requirements

### Functional Requirements
- **Product Catalog**: Product listing, search, filtering, categories, reviews, ratings
- **Shopping Cart**: Add/remove items, quantity updates, persistent across sessions
- **Order Processing**: Order creation, status tracking, cancellation, returns
- **Payment Integration**: Multiple payment methods (card, PayPal, wallet), refunds
- **Inventory Management**: Stock tracking, low-stock alerts, warehouse management
- **Shipping**: Address management, shipping methods, tracking, delivery estimates
- **User Management**: Accounts, order history, wishlists, addresses
- **Reviews & Ratings**: Product reviews, ratings, Q&A, image uploads
- **Recommendations**: Personalized product recommendations based on browsing/purchase history

### Non-Functional Requirements
- **Scale**: 10M+ products; 100K+ orders/day; 1M+ concurrent users
- **Latency**: Product search < 500ms; cart operations < 200ms; checkout < 2s
- **Availability**: 99.99% uptime; checkout must never lose data
- **Consistency**: Strong consistency for inventory and payments; eventual for reviews
- **Security**: PCI-DSS compliance for payments; GDPR for user data
- **Global**: Multi-currency, multi-language, multi-region deployment

## Key Design Decisions
- **Microservices**: Catalog, Cart, Order, Payment, Inventory, Shipping, Review services
- **Database**: PostgreSQL for orders/payments (ACID); Cassandra for catalog/reviews (scale)
- **Search**: Elasticsearch for product search with faceting and autocomplete
- **Cache (Redis)**: Product cache, session cart, rate limiting, inventory counters
- **Message Queue (Kafka)**: Order events, inventory updates, notifications
- **Payment**: Stripe/Adyen integration with idempotent charge operations
- **Inventory**: Optimistic locking to prevent overselling; reserved stock during checkout
